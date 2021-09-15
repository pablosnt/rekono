import os
import shutil
import subprocess
import sys
import uuid

import django_rq
from django.utils import timezone
from executions.enums import ParameterKey, Status
from executions.models import Execution, Target
from tools import utils
from tools.arguments import formatter
from tools.enums import FindingType
from tools.exceptions import (InstallationNotFoundException,
                              InvalidToolParametersException,
                              UnexpectedToolExitCodeException)
from tools.models import Configuration, Input, Intensity, Tool

from rekono.settings import EXECUTION_OUTPUTS
from findings import consumer


class BaseTool():

    file_output_enabled = False
     
    def __init__(
        self,
        tool: Tool,
        configuration: Configuration,
        inputs: list,
        intensity: Intensity
    ) -> None:
        self.tool = tool
        self.configuration = configuration
        self.inputs = inputs
        self.intensity = intensity
        self.filename_output = str(uuid.uuid4())
        self.directory_output = EXECUTION_OUTPUTS

    def check_installation(self) -> None:
        if self.tool.command and shutil.which(self.tool.command) is None:
            raise InstallationNotFoundException(
                f'Tool {self.tool.name} is not installed in the system'
            )

    def check_execution_condition(
        self,
        target: Target,
        target_ports: list,
        parameters: list,
        previous_findings: list
    ) -> bool:
        return True

    def clean_parameters(
        self,
        target_ports: list,
        parameters: list,
        previous_findings: list
    ) -> tuple:
        return (target_ports, parameters, previous_findings)
    
    def get_arguments(
        self,
        target: Target,
        target_ports: list,
        parameters: list,
        previous_findings: list
    ) -> str:
        command_arguments = {
            'intensity': self.intensity.argument,
            'output': '' if not self.file_output_enabled else os.path.join(
                self.directory_output,
                self.filename_output
            )
        }
        for i in self.inputs:
            try:
                if i.type == FindingType.TARGET:
                    command_arguments[i.name] = formatter.argument_with_target(
                        i.argument,
                        target.target
                    )
                    continue
                elif i.type == FindingType.TARGET_PORT:
                    command_arguments[i.name] = formatter.argument_with_target_ports(
                        i.argument,
                        target_ports
                    )
                    continue
                if i.selection == Input.InputSelection.FOR_EACH:
                    for r in previous_findings:
                        if isinstance(r, getattr(sys.modules[__name__], i.type)):
                            command_arguments[i.name] = formatter.argument_with_result(
                                i.argument,
                                r
                            )
                            break
                    if i.name not in command_arguments:
                        req_keys = utils.get_keys_from_argument(i.argument)
                        done_keys = []
                        for p in parameters:
                            if (
                                ParameterKey(p.key).name.lower() in req_keys and
                                p.key not in done_keys
                            ):
                                command_arguments[i.name] = formatter.argument_with_parameter(
                                    i.argument,
                                    p
                                )
                                done_keys.append(p.key)
                else:
                    findings = []
                    for r in previous_findings:
                        if isinstance(r, getattr(sys.modules[__name__], i.type)):
                            findings.append(r)
                    command_arguments[i.name] = formatter.argument_with_findings(
                        i.argument,
                        findings
                    )
            except KeyError:
                if i.required and i.name not in command_arguments:
                    raise InvalidToolParametersException(
                        f'Tool configuration requires {i.name} argument'
                    )
                elif not i.required and i.name not in command_arguments:
                    command_arguments[i.name] = ''
            if i.required and i.name not in command_arguments:
                raise InvalidToolParametersException(
                    f'Tool configuration requires {i.name} argument'
                )
        args = self.configuration.arguments.format(**command_arguments)
        if ' ' in args:
            args = args.split(' ')
            args = [arg for arg in args if arg]
        else:
            args = [args]
        return args

    def tool_execution(
        self,
        target: Target,
        target_ports: list,
        args: list,
        parameters: list,
        previous_findings: list
    ) -> tuple:
        args.insert(0, self.tool.command)
        result = subprocess.run(args, capture_output=True)
        if result.returncode > 0:
            raise UnexpectedToolExitCodeException(
                f'Exit code {result.returncode} during {self.tool.name} execution'
            )
        return result.stdout

    def parse_output(self, output: str) -> list:
        return []

    def send_findings(self, execution: Execution, findings: list) -> None:
        result_queue = django_rq.get_queue('finding-queue')
        result_queue.enqueue(consumer.get_findings, execution=execution, findings=findings)

    def on_start(self, execution: Execution) -> None:
        execution.start = timezone.now()
        execution.save()

    def on_skipped(self, execution: Execution) -> None:
        execution.status = Status.SKIPPED
        execution.end = timezone.now()
        execution.save()

    def on_running(self, execution: Execution) -> None:
        execution.status = Status.RUNNING
        execution.save()

    def on_error(self, execution: Execution) -> None:
        execution.status = Status.ERROR
        execution.end = timezone.now()
        execution.save()

    def on_completed(self, execution: Execution, output: str) -> None:
        execution.status = Status.COMPLETED
        execution.end = timezone.now()
        full_path = os.path.join(self.directory_output, self.filename_output)
        if self.file_output_enabled and os.path.isfile(full_path):
            execution.output_file = full_path
        execution.output_plain = output
        execution.save()

    def run(
        self,
        target: Target,
        target_ports: list,
        execution: Execution,
        parameters: list = [],
        previous_findings: list = []
    ) -> None:
        self.on_start(execution)
        try:
            self.check_installation()
        except InstallationNotFoundException:
            self.on_error(execution)
            return
        if not self.check_execution_condition(
            target,
            target_ports,
            parameters,
            previous_findings
        ):
            self.on_skipped(execution)
            return
        target_ports, parameters, previous_findings = self.clean_parameters(
            target_ports,
            parameters,
            previous_findings
        )
        try:
            args = self.get_arguments(
                target,
                target_ports,
                parameters,
                previous_findings
            )
        except InvalidToolParametersException:
            self.on_skipped(execution)
            return
        self.on_running(execution)
        try:
            output = self.tool_execution(
                target,
                target_ports,
                args,
                parameters,
                previous_findings
            )
        except Exception:
            self.on_error(execution)
            return
        self.on_completed(execution, output)
        findings = self.parse_output(output)
        self.send_findings(execution, findings)

import importlib
import os
import shutil
import subprocess
import uuid

from django.utils import timezone
from executions.enums import ParameterKey, Status
from executions.models import Execution, Target
from tools import utils
from tools.arguments import checker, formatter
from tools.enums import FindingType
from tools.exceptions import (InstallationNotFoundException,
                              InvalidToolParametersException,
                              UnexpectedToolExitCodeException)
from tools.models import Configuration, Input, Intensity, Tool
from queues.findings import producer

from rekono.settings import EXECUTION_OUTPUTS


class BaseTool():

    file_output_enabled = False
    ignore_exit_code = False
    file_output_extension = ''
     
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
        self.filename_output = str(uuid.uuid4()) + self.file_output_extension
        self.directory_output = EXECUTION_OUTPUTS
        self.path_output = os.path.join(self.directory_output, self.filename_output)

    def check_installation(self) -> None:
        if self.tool.command and shutil.which(self.tool.command) is None:
            raise InstallationNotFoundException(
                f'Tool {self.tool.name} is not installed in the system'
            )

    def prepare_environment(self, execution: Execution) -> None:
        pass

    def clean_environment(self, execution: Execution) -> None:
        pass

    def prepare_parameters(
        self,
        target: Target,
        target_ports: list,
        parameters: list,
        previous_findings: list
    ) -> tuple:
        expected_urls = [i for i in self.inputs if i.type == FindingType.URL]
        if expected_urls:
            url = utils.get_url_from_params(
                expected_urls[0],
                target,
                target_ports,
                previous_findings
            )
            if url:
                self.url = url
                previous_findings.append(url)
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
                aux = i.type.rsplit('.', 1)
                input_module = importlib.import_module(aux[0])
                input_class = getattr(input_module, aux[1])
                if i.selection == Input.InputSelection.FOR_EACH:
                    for r in previous_findings:
                        if isinstance(r, input_class):
                            if not checker.check_input_condition(i, r):
                                continue
                            command_arguments[i.name] = formatter.argument_with_finding(
                                i.argument,
                                r
                            )
                            break
                    if i.name not in command_arguments or i.type == FindingType.PARAMETER:
                        req_keys = utils.get_keys_from_argument(i.argument)
                        for p in parameters:
                            if ParameterKey(p.key).name.lower() in req_keys:
                                command_arguments[i.name] = formatter.argument_with_parameter(
                                    i.argument,
                                    p
                                )
                                break
                else:
                    if i.type != FindingType.PARAMETER:
                        findings = []
                        for r in previous_findings:
                            if isinstance(r, input_class) and checker.check_input_condition(i, r):
                                findings.append(r)
                        if findings:
                            command_arguments[i.name] = formatter.argument_with_findings(
                                i.argument,
                                findings
                            )
                    elif i.type == FindingType.PARAMETER or i.name not in command_arguments:
                        req_keys = utils.get_keys_from_argument(i.argument)
                        params = []
                        for p in parameters:
                            if ParameterKey(p.key).name.lower() in req_keys:
                                params.append(p)
                        if params:
                            command_arguments[i.name] = formatter.argument_with_parameters(
                                i.argument,
                                params
                            )
                if i.required and i.name not in command_arguments:
                    if i.type == FindingType.HOST:
                        if checker.check_input_condition(i, target):
                            command_arguments[i.name] = formatter.argument_with_target(
                                i.argument,
                                target.target
                            )
                            continue
                    elif i.type == FindingType.ENUMERATION:
                        command_arguments[i.name] = formatter.argument_with_target_ports(
                            i.argument,
                            target_ports
                        )
                        continue
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
            elif not i.required and i.name not in command_arguments:
                command_arguments[i.name] = ''
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
        exec = subprocess.run(args, capture_output=True)
        if (
            (not self.ignore_exit_code and exec.returncode > 0) or
            (self.ignore_exit_code and exec.returncode > 0 and not exec.stderr)
        ):
            raise UnexpectedToolExitCodeException(exec.stderr)
        return exec.stdout

    def parse_output(self, output: str) -> list:
        return []

    def send_findings(self, execution: Execution, findings: list) -> None:
        producer.create_findings(execution, findings)

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

    def on_error(self, execution: Execution, stderror: str = None) -> None:
        if stderror:
            execution.output_error = stderror
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
        except InstallationNotFoundException as ex:
            self.on_error(execution, stderror=str(ex))
            return
        target_ports, parameters, previous_findings = self.prepare_parameters(
            target,
            target_ports,
            parameters,
            previous_findings
        )
        try:
            args = self.get_arguments(target, target_ports, parameters, previous_findings)
        except InvalidToolParametersException as ex:
            print(ex)
            self.on_skipped(execution)
            return
        self.prepare_environment(execution)
        self.on_running(execution)
        try:
            output = self.tool_execution(target, target_ports, args, parameters, previous_findings)
        except UnexpectedToolExitCodeException as ex:
            self.on_error(execution, stderror=str(ex))
            self.clean_environment(execution)
            return
        except Exception as ex:
            print(ex)
            self.on_error(execution)
            self.clean_environment(execution)
            return
        self.clean_environment(execution)
        self.on_completed(execution, output)
        findings = self.parse_output(output)
        self.send_findings(execution, findings)

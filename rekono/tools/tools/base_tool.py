import os
import shutil
import subprocess
import uuid

from django.utils import timezone
from tasks.enums import ParameterKey, Status
from executions.models import Execution
from findings.queue import producer
from tools import utils
from tools.arguments import checker, formatter
from tools.arguments.constants import TARGET
from tools.enums import FindingType
from tools.exceptions import (InstallationNotFoundException,
                              InvalidToolParametersException,
                              UnexpectedToolExitCodeException)
from tools.models import Configuration, Input, Intensity, Tool
from tools.enums import InputSelection

from rekono.settings import EXECUTION_OUTPUTS


class BaseTool():

    ignore_exit_code = False
    findings = []
    findings_relations = {}
     
    def __init__(
        self,
        execution: Execution,
        tool: Tool,
        configuration: Configuration,
        inputs: list,
        intensity: Intensity
    ) -> None:
        execution.rq_job_pid = os.getpid()
        execution.save()
        self.execution = execution
        self.target = execution.task.target
        self.target_ports = self.target.target_ports.all()
        self.tool = tool
        self.configuration = configuration
        self.inputs = inputs
        self.intensity = intensity
        self.file_output_enabled = self.tool.output_format != None
        self.file_output_extension = self.tool.output_format or 'txt'
        self.filename_output = f'{str(uuid.uuid4())}.{self.file_output_extension}'
        self.directory_output = EXECUTION_OUTPUTS
        self.path_output = os.path.join(self.directory_output, self.filename_output)

    def check_installation(self) -> None:
        if self.tool.command and shutil.which(self.tool.command) is None:
            raise InstallationNotFoundException(
                f'Tool {self.tool.name} is not installed in the system'
            )

    def prepare_environment(self) -> None:
        pass

    def clean_environment(self) -> None:
        pass

    def prepare_parameters(self, parameters: list, previous_findings: list) -> tuple:
        return (parameters, previous_findings)
    
    def get_arguments(self, parameters: list, previous_findings: list) -> str:
        command_arguments = {
            'intensity': self.intensity.argument,
            'output': '' if not self.file_output_enabled else os.path.join(
                self.directory_output,
                self.filename_output
            )
        }
        for i in self.inputs:
            try:
                req_keys = utils.get_keys_from_argument(i.argument)
                input_class = utils.get_finding_class_by_type(i.type)
                if i.selection == InputSelection.FOR_EACH:
                    for r in previous_findings:
                        if isinstance(r, input_class):
                            if not checker.check_input_condition(i, r):
                                continue
                            command_arguments[i.name] = formatter.argument_with_one(i.argument, r)
                            self.findings_relations[input_class.__name__.lower()] = r
                            break
                    if i.name not in command_arguments or i.type == FindingType.PARAMETER:
                        for p in parameters:
                            if ParameterKey(p.key).name.lower() in req_keys:
                                command_arguments[i.name] = formatter.argument_with_one(
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
                            command_arguments[i.name] = formatter.argument_with_multiple(
                                i.argument,
                                findings
                            )
                    elif i.type == FindingType.PARAMETER or i.name not in command_arguments:
                        params = []
                        for p in parameters:
                            if ParameterKey(p.key).name.lower() in req_keys:
                                params.append(p)
                        if params:
                            command_arguments[i.name] = formatter.argument_with_multiple(
                                i.argument,
                                params
                            )
                if (
                    i.name not in command_arguments and
                    (
                        i.type == FindingType.HOST or 
                        (i.type == FindingType.ENUMERATION and i.name == TARGET)
                    ) and
                    checker.check_input_condition(i, self.target)
                ):
                    command_arguments[i.name] = formatter.argument_with_one(
                        i.argument,
                        self.target
                    )
                    continue
                if (
                    i.name not in command_arguments and
                    i.type == FindingType.ENUMERATION and self.target_ports
                ):
                    command_arguments[i.name] = formatter.argument_with_target_ports(
                        i.argument,
                        self.target_ports,
                        self.target
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

    def tool_execution(self, args: list, parameters: list, previous_findings: list) -> str:
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

    def process_findings(self) -> None:
        for finding in self.findings:
            for key, value in self.findings_relations.items():
                if hasattr(finding, key):
                    setattr(finding, key, value)

    def send_findings(self, domain: str) -> None:
        producer(self.execution, self.findings, domain)

    def on_start(self) -> None:
        self.execution.start = timezone.now()
        self.execution.save()
        if not self.execution.task.start:
            self.execution.task.status = Status.RUNNING
            self.execution.task.start = timezone.now()
            self.execution.task.save()

    def on_skipped(self) -> None:
        self.execution.status = Status.SKIPPED
        self.execution.end = timezone.now()
        self.execution.save()

    def on_running(self) -> None:
        self.execution.status = Status.RUNNING
        self.execution.save()

    def on_error(self, stderror: str = None) -> None:
        if stderror:
            self.execution.output_error = stderror
        self.execution.status = Status.ERROR
        self.execution.end = timezone.now()
        self.execution.save()

    def on_completed(self, output: str) -> None:
        self.execution.status = Status.COMPLETED
        self.execution.end = timezone.now()
        full_path = os.path.join(self.directory_output, self.filename_output)
        if self.file_output_enabled and os.path.isfile(full_path):
            self.execution.output_file = full_path
        self.execution.output_plain = output
        self.execution.save()

    def run(self, parameters: list = [], previous_findings: list = [], domain: str = None) -> None:
        self.on_start()
        try:
            self.check_installation()
        except InstallationNotFoundException as ex:
            self.on_error(stderror=str(ex))
            return
        parameters, previous_findings = self.prepare_parameters(
            parameters,
            previous_findings
        )
        try:
            args = self.get_arguments(parameters, previous_findings)
        except InvalidToolParametersException as ex:
            print(ex)
            self.on_skipped()
            return
        self.prepare_environment()
        self.on_running()
        try:
            output = self.tool_execution(args, parameters, previous_findings)
        except UnexpectedToolExitCodeException as ex:
            self.on_error(stderror=str(ex))
            self.clean_environment()
            return
        except Exception as ex:
            print(ex)
            self.on_error()
            self.clean_environment()
            return
        self.clean_environment()
        self.on_completed(output)
        self.findings = self.parse_output(output)
        self.process_findings()
        self.send_findings(domain)

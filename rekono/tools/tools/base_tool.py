import os
import shutil
import subprocess
import uuid

from django.utils import timezone
from executions.enums import ParameterKey, Status
from executions.models import Execution
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
        self.findings = []
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
        expected_urls = [i for i in self.inputs if i.type == FindingType.URL]
        if expected_urls:
            url = utils.get_url_from_params(
                expected_urls[0],
                self.target,
                self.target_ports,
                previous_findings
            )
            if url:
                self.url = url
                previous_findings.append(url)
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
                input_class = utils.get_finding_class_by_type(i.type)
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
                if i.name not in command_arguments:
                    if i.type == FindingType.HOST:
                        if checker.check_input_condition(i, self.target):
                            command_arguments[i.name] = formatter.argument_with_target(
                                i.argument,
                                self.target.target
                            )
                            continue
                    elif i.type == FindingType.ENUMERATION and self.target_ports:
                        command_arguments[i.name] = formatter.argument_with_target_ports(
                            i.argument,
                            self.target_ports
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

    def send_findings(self) -> None:
        producer.process_findings(self.execution, self.findings)

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

    def run(self, parameters: list = [], previous_findings: list = []) -> None:
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
        self.send_findings()

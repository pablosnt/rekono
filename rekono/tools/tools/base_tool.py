import os
import shutil
import subprocess
import uuid

from arguments import checker, formatter
from django.utils import timezone
from executions.models import Execution
from findings.models import Vulnerability
from findings.queue import producer
from tasks.enums import Status
from tools import utils
from tools.enums import InputSelection
from tools.exceptions import (InstallationNotFoundException,
                              InvalidToolParametersException,
                              UnexpectedToolExitCodeException)
from tools.models import Configuration, Input, Intensity, Tool

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
        self.tool = tool
        self.configuration = configuration
        self.inputs = inputs
        self.intensity = intensity
        self.file_output_enabled = self.tool.output_format is not None
        self.file_output_extension = self.tool.output_format or 'txt'
        self.filename_output = f'{str(uuid.uuid4())}.{self.file_output_extension}'
        self.path_output = os.path.join(EXECUTION_OUTPUTS, self.filename_output)

    def check_installation(self) -> None:
        if self.tool.command and shutil.which(self.tool.command) is None:
            raise InstallationNotFoundException(
                f'Tool {self.tool.name} is not installed in the system'
            )

    def prepare_environment(self) -> None:
        pass    # This method can be implemented by specific tools to run code before execution

    def clean_environment(self) -> None:
        pass    # This method can be implemented by specific tools to run code after execution

    def evaluate_arguments_error(self, name: str, required: bool, arguments: dict):
        if required and name not in arguments:
            raise InvalidToolParametersException(f'Tool configuration requires {name} argument')
        return arguments[name] if name in arguments else ''

    def get_arguments(self, targets: list, previous_findings: list) -> list:
        command_arguments = {
            'intensity': self.intensity.argument,
            'output': self.path_output if self.file_output_enabled else ''
        }
        for i in self.inputs:
            try:
                input_classes = utils.get_finding_class_by_input_type(i.type)
                findings = []
                for source in [previous_findings, targets]:
                    for r in source:
                        for input_class in input_classes:
                            if isinstance(r, input_class) and checker.check_finding(i, r):
                                if i.selection == InputSelection.FOR_EACH:
                                    command_arguments[i.name] = formatter.argument_with_one(i.argument, r)      # noqa: E501
                                    self.findings_relations[input_class.__name__.lower()] = r
                                    break
                                else:
                                    findings.append(r)
                    if findings:
                        command_arguments[i.name] = formatter.argument_with_multiple(i.argument, findings)  # noqa: E501
                    if i.name in command_arguments:
                        break
            except KeyError:
                command_arguments[i.name] = self.evaluate_arguments_error(
                    i.name,
                    i.required,
                    command_arguments
                )
            command_arguments[i.name] = self.evaluate_arguments_error(
                i.name,
                i.required,
                command_arguments
            )
        args = self.configuration.arguments.format(**command_arguments)
        return [arg for arg in args.split(' ') if arg] if ' ' in args else [args]

    def tool_execution(self, args: list, targets: list, previous_findings: list) -> str:
        args.insert(0, self.tool.command)
        exec = subprocess.run(args, capture_output=True)
        if (
            (not self.ignore_exit_code and exec.returncode > 0)
            or (self.ignore_exit_code and exec.returncode > 0 and not exec.stderr)
        ):
            raise UnexpectedToolExitCodeException(exec.stderr)
        return exec.stdout

    def parse_output(self, output: str) -> list:
        return []

    def process_findings(self) -> None:
        for finding in self.findings:
            for key, value in self.findings_relations.items():
                if (
                    isinstance(finding, Vulnerability)
                    and getattr(finding, 'technology')
                    and key == 'enumeration'
                ):
                    continue
                elif (
                    isinstance(finding, Vulnerability)
                    and getattr(finding, 'enumeration')
                    and key == 'technology'
                ):
                    setattr(finding, 'enumeration', None)
                if hasattr(finding, key):
                    setattr(finding, key, value)

    def send_findings(self, rekono_address: str) -> None:
        producer(self.execution, self.findings, rekono_address)

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

    def on_error(self, stderror: bytes = None) -> None:
        if stderror:
            self.execution.output_error = stderror.decode('utf-8')
        self.execution.status = Status.ERROR
        self.execution.end = timezone.now()
        self.execution.save()

    def on_completed(self, output: bytes) -> None:
        self.execution.status = Status.COMPLETED
        self.execution.end = timezone.now()
        if self.file_output_enabled and os.path.isfile(self.path_output):
            self.execution.output_file = self.path_output
        self.execution.output_plain = output.decode('utf-8')
        self.execution.save()

    def run(self, targets: list = [], previous_findings: list = [], rekono_address: str = None) -> None:
        self.on_start()
        try:
            self.check_installation()
        except InstallationNotFoundException as ex:
            self.on_error(stderror=str(ex))
            return
        try:
            args = self.get_arguments(targets, previous_findings)
        except InvalidToolParametersException as ex:
            print(ex)
            self.on_skipped()
            return
        self.prepare_environment()
        self.on_running()
        try:
            output = self.tool_execution(args, targets, previous_findings)
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
        if self.file_output_enabled and os.path.isfile(self.path_output):
            self.findings = self.parse_output(output)
            self.process_findings()
            self.send_findings(rekono_address)

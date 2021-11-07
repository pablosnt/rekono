import os
import shutil
import subprocess
import uuid

from arguments import checker, formatter
from arguments.enums import Keyword
from django.utils import timezone
from executions.models import Execution
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
        intensity: Intensity,
        target_ports: list
    ) -> None:
        execution.rq_job_pid = os.getpid()
        execution.save()
        self.execution = execution
        self.target = execution.task.target
        self.target_ports = target_ports if target_ports else self.target.target_ports.all()
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

    def prepare_findings(self, manual_findings: list, previous_findings: list) -> tuple:
        return (manual_findings, previous_findings)

    def evaluate_use_of_target(self, input: Input, arguments: dict) -> bool:
        return (
            input.name not in arguments
            and checker.check_finding(input, self.target)
            and input.name in [
                Keyword.TARGET.name.lower(),
                Keyword.HOST.name.lower(),
                Keyword.URL.name.lower()
            ]
        )

    def evaluate_use_of_target_ports(self, input: Input, arguments: dict) -> bool:
        return (
            input.name not in arguments
            and self.target_ports
            and input.name in [
                Keyword.PORT.name.lower(),
                Keyword.PORTS.name.lower(),
                Keyword.PORTS_COMMAS.name.lower(),
                Keyword.URL.name.lower()
            ]
        )

    def evaluate_arguments_error(self, name: str, required: bool, arguments: dict):
        if required and name not in arguments:
            raise InvalidToolParametersException(
                f'Tool configuration requires {name} argument'
            )
        return arguments[name] if name in arguments else ''

    def get_arguments(self, manual_findings: list, previous_findings: list) -> list:
        command_arguments = {
            'intensity': self.intensity.argument,
            'output': self.path_output if self.file_output_enabled else ''
        }
        for i in self.inputs:
            try:
                input_class = utils.get_finding_class_by_type(i.type)
                findings = []
                for source in [previous_findings, manual_findings]:
                    for r in source:
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
                if self.evaluate_use_of_target(i, command_arguments):
                    command_arguments[i.name] = formatter.argument_with_one(i.argument, self.target)
                elif self.evaluate_use_of_target_ports(i, command_arguments):
                    command_arguments[i.name] = formatter.argument_with_target_ports(
                        i.argument,
                        self.target_ports,
                        self.target
                    )
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

    def tool_execution(self, args: list, manual_findings: list, previous_findings: list) -> str:
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
        if self.file_output_enabled and os.path.isfile(self.path_output):
            self.execution.output_file = self.path_output
        self.execution.output_plain = output
        self.execution.save()

    def run(
        self,
        manual_findings: list = [],
        previous_findings: list = [],
        domain: str = None
    ) -> None:
        self.on_start()
        try:
            self.check_installation()
        except InstallationNotFoundException as ex:
            self.on_error(stderror=str(ex))
            return
        manual_findings, previous_findings = self.prepare_findings(
            manual_findings,
            previous_findings
        )
        try:
            args = self.get_arguments(manual_findings, previous_findings)
        except InvalidToolParametersException as ex:
            print(ex)
            self.on_skipped()
            return
        self.prepare_environment()
        self.on_running()
        try:
            output = self.tool_execution(args, manual_findings, previous_findings)
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
            self.send_findings(domain)

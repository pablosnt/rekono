import os
import shutil
import subprocess
import uuid
from typing import Any, List, Union

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models import Model
from django.utils import timezone
from executions.models import Execution
from findings.models import Vulnerability
from findings.queue import producer
from findings.utils import get_unique_filter
from input_types.base import BaseInput
from tasks.enums import Status
from tools import utils
from tools.exceptions import (InstallationNotFoundException,
                              InvalidToolParametersException,
                              UnexpectedToolExitCodeException)
from tools.models import Argument, Configuration, Input, Intensity, Tool

from rekono.settings import EXECUTION_OUTPUTS


class BaseTool():

    ignore_exit_code = False
    # findings = []
    # findings_relations = {}

    def __init__(
        self,
        execution: Execution,
        tool: Tool,
        configuration: Configuration,
        arguments: list,
        intensity: Intensity
    ) -> None:
        execution.rq_job_pid = os.getpid()
        execution.save()
        self.execution = execution
        self.tool = tool
        self.configuration = configuration
        self.arguments = arguments
        self.intensity = intensity
        self.file_output_enabled = self.tool.output_format is not None
        self.file_output_extension = self.tool.output_format or 'txt'
        self.filename_output = f'{str(uuid.uuid4())}.{self.file_output_extension}'
        self.path_output = os.path.join(EXECUTION_OUTPUTS, self.filename_output)
        self.findings = []
        self.findings_relations = {}

    def check_installation(self) -> None:
        if self.tool.command and shutil.which(self.tool.command) is None:
            raise InstallationNotFoundException(
                f'Tool {self.tool.name} is not installed in the system'
            )

    def prepare_environment(self) -> None:
        pass    # This method can be implemented by specific tools to run code before execution

    def clean_environment(self) -> None:
        pass    # This method can be implemented by specific tools to run code after execution
    
    def format(self, argument: Argument, findings: Union[List[BaseInput], BaseInput]) -> str:
        data = {}
        if argument.multiple and isinstance(findings, List):
            for finding in findings:
                data = finding.parse(data)
        else:
            data = findings.parse()
        data = {k: v for k, v in data.items() if v}
        try:
            return argument.argument.format(**data)
        except KeyError:
            return None

    def process_source(self, argument: Argument, input: Input, model: Model, source: list, command: dict) -> dict:
        selection = []
        for item in source:
            if isinstance(item, model) and item.filter(input):
                if argument.multiple:
                    selection.append(item)
                else:
                    command[argument.name] = self.format(argument, item)
                    self.findings_relations[model.__name__.lower()] = item
                    return command
        if selection:
            formatted_argument = self.format(argument, selection)
            if formatted_argument:
                command[argument.name] = formatted_argument
        return command
                

    def get_arguments(self, targets: list, previous_findings: list) -> list:
        command = {
            'intensity': self.intensity.argument,
            'output': self.path_output if self.file_output_enabled else ''
        }
        for argument in self.arguments:
            for input in argument.inputs.order_by('order'):
                model = input.type.get_related_model_class()
                command = self.process_source(argument, input, model, previous_findings, command)
                if argument.name in command and command[argument.name]:
                    break
            if argument.name not in command or not command[argument.name]:
                for input in argument.inputs.order_by('order'):
                    model = input.type.get_callback_target_class()
                    command = self.process_source(argument, input, model, targets, command)
                    if argument.name in command and command[argument.name]:
                        break
            if argument.name not in command or not command[argument.name]:
                if argument.required:
                    raise InvalidToolParametersException(
                        f'Tool configuration requires {argument.name} argument'
                    )
                else:
                    command[argument.name] = ''
        args = self.configuration.arguments.format(**command)
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

    def create_finding(self, finding_type: Any, **fields) -> Any:
        finding = None
        fields['execution'] = self.execution
        try:
            finding = finding_type.objects.create(**fields)
            finding.save()
        except ValidationError as e:
            if 'Unique constraint violation' in e.message:
                unique_filter = get_unique_filter(finding_type.key_fields, fields, self.execution)
                finding = finding_type.objects.filter(**unique_filter).first()
                fields.pop('execution')
                for field, value in fields.items():
                    if value and value != getattr(finding, field):
                        setattr(finding, field, value)
                finding.save()
        self.findings.append(finding)
        return finding

    def parse_output(self, output: str) -> None:
        pass    # This method should be implemented by specific tools to parse the output

    def process_findings(self) -> None:
        for finding in self.findings:
            if (
                isinstance(finding, Vulnerability)
                and getattr(finding, 'enumeration')
                and 'technology' in self.findings_relations
            ):
                setattr(finding, 'enumeration', None)
            for key, value in self.findings_relations.items():
                if (
                    isinstance(finding, Vulnerability)
                    and getattr(finding, 'technology')
                    and key == 'enumeration'
                ):
                    continue
                if hasattr(finding, key):
                    setattr(finding, key, value)

    def send_findings(self) -> None:
        producer(self.execution, self.findings)

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

    def run(self, targets: list = [], previous_findings: list = []) -> None:
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
            self.parse_output(output)
            self.process_findings()
            self.send_findings()

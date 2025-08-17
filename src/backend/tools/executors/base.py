import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any

from django.forms.models import model_to_dict
from django.utils import timezone

from authentications.models import Authentication
from executions.enums import Status
from executions.models import Execution
from findings.framework.models import Finding
from findings.models import Port
from framework.enums import InputKeyword
from framework.logging import LoggingEntity
from http_headers.models import HttpHeader
from parameters.models import InputTechnology, InputVulnerability
from rekono.settings import CONFIG
from security.cryptography import Crypto
from settings.models import Settings
from target_ports.models import TargetPort
from tools.models import Intensity
from wordlists.models import Wordlist


class BaseExecutor(LoggingEntity):
    arguments = []
    environment = {}
    findings_used_in_execution = {}
    targets_used_in_execution = {}
    authentication = None

    def __init__(self, execution: Execution) -> None:
        self.execution = execution
        self.intensity = (
            Intensity.objects.filter(tool=execution.configuration.tool, value__lte=execution.task.intensity)
            .order_by("-value")
            .first()
        )
        self.report = CONFIG.reports / f"{str(uuid.uuid4())}.{execution.configuration.tool.output_format or 'txt'}"
        self.execution_directory = (
            getattr(CONFIG, self.execution.configuration.tool.run_directory_property.lower())
            if self.execution.configuration.tool.run_directory_property
            else None
        )

    def get_arguments(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> list[str]:
        parameters = {
            "script": (
                (
                    Path(
                        getattr(
                            CONFIG,
                            self.execution.configuration.tool.script_directory_property.lower(),
                        )
                    )
                    / self.execution.configuration.tool.script
                )
                if self.execution.configuration.tool.script_directory_property
                and self.execution.configuration.tool.script
                else ""
            ),
            "command": self.execution.configuration.tool.command,
            "intensity": self.intensity.argument,
            "output": self.report if self.execution.configuration.tool.output_format else "",
        }
        for argument in self.execution.configuration.tool.arguments.all():
            for argument_input in argument.inputs.all().order_by("order"):
                parsed_data: dict[str, Any] = {}
                for base_input in (
                    findings
                    + list(wordlists)
                    + list(
                        Authentication.objects.filter(
                            target_port__target=self.execution.task.target,
                            target_port__port__in=[
                                f.port if isinstance(f, Port) else f.port.port
                                for f in findings
                                if isinstance(f, Port) or (hasattr(f, "port") and isinstance(f.port, Port))
                            ],
                        ).all()
                    )
                    + [self.execution.task.target]
                    + list(target_ports)
                    + [p.authentication for p in target_ports if hasattr(p, "authentication")]
                    + list(input_vulnerabilities)
                    + list(input_technologies)
                    + list(HttpHeader.objects.filter(target__isnull=True, user__isnull=True).all())
                    + list(self.execution.task.executor.http_headers.all())
                    + list(self.execution.task.target.http_headers.all())
                ):
                    is_fallback = argument_input.type.fallback_model_class and isinstance(
                        base_input, argument_input.type.fallback_model_class
                    )
                    if is_fallback and parsed_data:
                        break
                    is_model = argument_input.type.model_class and isinstance(
                        base_input, argument_input.type.model_class
                    )
                    if not is_model or is_fallback:
                        continue
                    if base_input.filter(argument_input, self.execution.task.target):
                        parsed_data = base_input.parse(parsed_data)
                        if is_fallback:
                            self.targets_used_in_execution[base_input.__class__] = base_input
                        else:
                            self.findings_used_in_execution[base_input.__class__] = base_input
                        if isinstance(base_input, Authentication):
                            self.authentication = base_input
                        if not argument.multiple:
                            break
                if parsed_data:
                    break
            if parsed_data:
                if InputKeyword.HEADERS.name.lower() in parsed_data:
                    parameters[argument.name] = " ".join(
                        [
                            argument.argument.format(
                                **{
                                    InputKeyword.HEADER_KEY.name.lower(): k,
                                    InputKeyword.HEADER_VALUE.name.lower(): v,
                                }
                            )
                            for k, v in parsed_data.get(InputKeyword.HEADERS.name.lower(), {}).items()
                        ]
                    )
                else:
                    parameters[argument.name] = argument.argument.format(**parsed_data)
            elif not argument.required:
                parameters[argument.name] = ""
            else:
                raise RuntimeError(f"Argument '{argument.name}' is required to execute tool '{argument.tool.name}'")
        return [
            a.replace('"', "")
            for a in re.findall(
                r'[^\s\'"]*[\'"][^\'"]+[\'"]|[^\'"\s]+', self.execution.configuration.arguments.format(**parameters)
            )
        ]

    def check_arguments(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> bool:
        try:
            self.get_arguments(findings, target_ports, input_vulnerabilities, input_technologies, wordlists)
            return True
        except RuntimeError:
            return False

    def get_environment(self) -> dict[str, Any]:
        environment = os.environ.copy()
        if self.execution.configuration.tool.command not in self.arguments:
            self.arguments.insert(0, self.execution.configuration.tool.command)
        else:
            index = self.arguments.index(self.execution.configuration.tool.command)
            for definition in self.arguments[:index]:
                if "=" in definition:
                    variable, value = definition.split("=", 1)
                    environment[variable] = value.strip().replace("'", "").replace('"', "")
            self.arguments = self.arguments[index:]
        settings = Settings.objects.first()
        for proxy in model_to_dict(Settings).keys():
            if "_proxy" in proxy and getattr(settings, proxy) is not None:
                environment[proxy.upper()] = getattr(settings, proxy)
        return environment

    def before_running(self) -> None:
        pass

    def run_tool(self, environment: dict[str, Any] = os.environ.copy()) -> None:
        self.logger.info(f"[Tool] Running: {' '.join(self.arguments)}")
        stdout = (
            self.report
            if self.execution.configuration.tool.output_format
            and not any([str(self.report) in arg for arg in self.arguments])
            else None
        )
        if stdout:
            with self.report.open("w") as _stdout:
                # Stderr is discarded as the stdout file will be used as stdout
                # and report, so stderr content would break the report format
                process = subprocess.run(self.arguments, stdout=_stdout, env=environment, cwd=self.execution_directory)
            output = ""
            if self.report.is_file():
                with self.report.open("r") as _output:
                    output = _output.read()
        else:
            process = subprocess.run(
                self.arguments,
                env=environment,
                cwd=self.execution_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output = process.stdout
        if self.execution.configuration.tool.output_format and self.report.is_file():
            self.execution.output_file = self.report
        # Remove ANSI colors from tool outputs
        self.execution.output_plain = re.sub(r"(\x9B|\x1B\[)[\d]*[ -\/]*[@-~]", "", output, flags=re.IGNORECASE)
        self.execution.save(update_fields=["output_plain", "output_file"])
        if not self.execution.configuration.tool.ignore_exit_code and process.returncode > 0:
            self.on_error()
        else:
            self.on_completed()

    def after_running(self) -> None:
        pass

    def on_start(self) -> None:
        self.execution.status = Status.RUNNING
        self.execution.start = timezone.now()
        self.execution.save(update_fields=["start", "status"])
        if not self.execution.task.start:
            self.execution.task.start = timezone.now()
            self.execution.task.save(update_fields=["start"])

    def on_skip(self, reason: str) -> None:
        self.execution.status = Status.SKIPPED
        self.execution.skipped_reason = reason
        self.execution.end = timezone.now()
        self.execution.save(update_fields=["status", "end", "skipped_reason"])
        self.on_task_end()

    def on_error(self) -> None:
        self.execution.status = Status.ERROR
        self.execution.end = timezone.now()
        self.execution.save(update_fields=["status", "end"])
        self.on_task_end()

    def on_completed(self) -> None:
        self.execution.status = Status.COMPLETED
        self.execution.end = timezone.now()
        self.execution.hash = Crypto.hash(
            " ".join(
                [f"{k}={v}" for k, v in self.environment.items()]
                + [a for a in self.arguments if str(self.report).lower() not in a.lower()]
            ).lower()
        )
        self.execution.save(update_fields=["status", "end", "hash"])
        self.on_task_end()

    def on_task_end(self) -> None:
        if not Execution.objects.filter(
            task=self.execution.task, status__in=[Status.REQUESTED, Status.RUNNING]
        ).exists():
            self.execution.task.end = timezone.now()
            self.execution.task.save(update_fields=["end"])
            self.logger.info(f"[Task] Task {self.execution.task.id} has finished")

    def execute(
        self,
        findings: list[Finding],
        target_ports: list[TargetPort],
        input_vulnerabilities: list[InputVulnerability],
        input_technologies: list[InputTechnology],
        wordlists: list[Wordlist],
    ) -> None:
        self.on_start()
        self.execution.configuration.tool.update_status()
        if not self.execution.configuration.tool.is_installed:
            self.on_skip(f"Tool {self.execution.configuration.tool.name} is not installed in the system")
            return
        try:
            self.arguments = self.get_arguments(
                findings, target_ports, input_vulnerabilities, input_technologies, wordlists
            )
        except RuntimeError as error:
            self.logger.error(f"[Tool] {str(error)}")
            self.on_skip(str(error))
            return
        self.environment = self.get_environment()
        self.before_running()
        try:
            if not CONFIG.testing:
                self.run_tool(self.environment)
        except (RuntimeError, Exception):
            self.logger.error(f"[Tool] {self.execution.configuration.tool.name} execution finished with errors")
            self.on_error()
            self.after_running()
            return
        self.after_running()
        self.on_completed()
        self.logger.info(f"[Tool] {self.execution.configuration.tool.name} execution has been completed")

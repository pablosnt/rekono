import logging
import os
import re
import subprocess  # nosec
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from authentications.models import Authentication
from django.forms.models import model_to_dict
from django.utils import timezone
from executions.enums import Status
from executions.models import Execution
from findings.framework.models import Finding
from findings.models import Port
from framework.enums import InputKeyword
from framework.models import BaseInput
from http_headers.models import HttpHeader
from parameters.models import InputTechnology, InputVulnerability
from rekono.settings import CONFIG
from settings.models import Settings
from target_ports.models import TargetPort
from tools.models import Intensity
from wordlists.models import Wordlist

logger = logging.getLogger()


class BaseExecutor:
    def __init__(self, execution: Execution) -> None:
        self.execution = execution
        self.intensity = (
            Intensity.objects.filter(
                tool=execution.configuration.tool, value__lte=execution.task.intensity
            )
            .order_by("-value")
            .first()
        )
        self.report = (
            CONFIG.reports
            / f'{str(uuid.uuid4())}.{execution.configuration.tool.output_format or "txt"}'
        )
        self.arguments: List[str] = []
        self.findings_used_in_execution: Dict[Any, BaseInput] = {}
        self.authentication: Optional[Authentication] = None

    def _get_arguments(
        self,
        findings: List[Finding],
        target_ports: List[TargetPort],
        input_vulnerabilities: List[InputVulnerability],
        input_technologies: List[InputTechnology],
        wordlists: List[Wordlist],
    ) -> List[str]:
        parameters = {
            "script": (
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
            else "",
            "command": self.execution.configuration.tool.command,
            "intensity": self.intensity.argument,
            "output": self.report
            if self.execution.configuration.tool.output_format
            else "",
        }
        for argument in self.execution.configuration.tool.arguments.all():
            for argument_input in argument.inputs.all().order_by("order"):
                input_model = argument_input.type.get_model_class()
                input_fallback = argument_input.type.get_fallback_model_class()
                parsed_data: Dict[str, Any] = {}
                for base_input in (
                    findings
                    + list(wordlists)
                    + list(
                        Authentication.objects.filter(
                            target_port__target=self.execution.task.target,
                            target_port__port__in=[
                                p.port for p in findings if isinstance(p, Port)
                            ],
                        ).all()
                    )
                    + [self.execution.task.target]
                    + list(target_ports)
                    + [p.authentication for p in target_ports]
                    + list(input_vulnerabilities)
                    + list(input_technologies)
                    + list(
                        HttpHeader.objects.filter(
                            target__isnull=True, user__isnull=True
                        ).all()
                    )
                    + list(self.execution.task.executor.http_headers.all())
                    + list(self.execution.task.target.http_headers.all())
                ):
                    is_fallback = input_fallback and isinstance(
                        base_input, input_fallback
                    )
                    if is_fallback and parsed_data:
                        break
                    is_model = input_model and isinstance(base_input, input_model)
                    if (is_model or is_fallback) and base_input.filter(
                        argument_input, self.execution.task.target
                    ):
                        parsed_data = base_input.parse(parsed_data)
                        self.findings_used_in_execution[
                            base_input.__class__
                        ] = base_input
                        if isinstance(base_input, Authentication):
                            self.authentication = base_input
                        if not argument.multiple:
                            break
                if parsed_data:
                    break
            if parsed_data:
                if InputKeyword.HEADERS.name.lower() in parsed_data:
                    parameters[argument.name] = " ".join([argument.argument.format(**{InputKeyword.HEADER_KEY.name.lower(): k, InputKeyword.HEADER_VALUE.name.lower(): v}) for k, v in parsed_data.get(InputKeyword.HEADERS.name.lower(), {}).items()])
                else:
                    parameters[argument.name] = argument.argument.format(**parsed_data)
            elif not argument.required:
                parameters[argument.name] = ""
            else:
                raise RuntimeError(
                    f"Argument '{argument.name}' is required to execute tool '{argument.tool.name}'"
                )
        return [
            a.replace('"', "")
            for a in re.findall(
                r'[^\s\'"]*[\'"][^\'"]+[\'"]|[^\'"\s]+',
                self.execution.configuration.arguments.format(**parameters),
            )
        ]

    def check_arguments(
        self,
        findings: List[Finding],
        target_ports: List[TargetPort],
        input_vulnerabilities: List[InputVulnerability],
        input_technologies: List[InputTechnology],
        wordlists: List[Wordlist],
    ) -> bool:
        try:
            self._get_arguments(
                findings,
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
            )
            return True
        except RuntimeError:
            return False

    def _get_environment(self) -> Dict[str, Any]:
        environment = os.environ.copy()
        if self.execution.configuration.tool.command not in self.arguments:
            self.arguments.insert(0, self.execution.configuration.tool.command)
        else:
            index = self.arguments.index(self.execution.configuration.tool.command)
            for definition in self.arguments[:index]:
                if "=" in definition:
                    variable, value = definition.split("=", 1)
                    environment[variable] = (
                        value.strip().replace("'", "").replace('"', "")
                    )
            self.arguments = self.arguments[index:]
        settings = Settings.objects.first()
        for proxy in model_to_dict(Settings).keys():
            if "_proxy" in proxy and getattr(settings, proxy) is not None:
                environment[proxy.upper()] = getattr(settings, proxy)
        return environment

    def _before_running(self) -> None:
        pass

    def _run(self, environment: Dict[str, Any] = os.environ.copy()) -> str:
        logger.info(f"[Tool] Running: {' '.join(self.arguments)}")
        process = subprocess.run(  # nosec
            self.arguments,
            capture_output=True,
            env=environment,
            cwd=getattr(
                CONFIG, self.execution.configuration.tool.run_directory_property.lower()
            )
            if self.execution.configuration.tool.run_directory_property
            else None,
        )
        if (
            not self.execution.configuration.tool.ignore_exit_code
            and process.returncode > 0
        ):
            raise RuntimeError(process.stderr.decode("utf-8"))
        return process.stdout.decode("utf-8")

    def _after_running(self) -> None:
        pass

    def _on_start(self) -> None:
        self.execution.start = timezone.now()
        self.execution.save(update_fields=["start"])
        if not self.execution.task.start:
            self.execution.task.start = timezone.now()
            self.execution.task.save(update_fields=["start"])

    def _on_task_end(self) -> None:
        if not Execution.objects.filter(
            task=self.execution.task, status__in=[Status.REQUESTED, Status.RUNNING]
        ).exists():
            self.execution.task.end = timezone.now()
            self.execution.task.save(update_fields=["end"])
            logger.info(f"[Task] Task {self.execution.task.id} has finished")

    def _on_skip(self, reason: str) -> None:
        self.execution.status = Status.SKIPPED
        self.execution.skipped_reason = reason
        self.execution.end = timezone.now()
        self.execution.save(update_fields=["status", "end", "skipped_reason"])
        self._on_task_end()

    def _on_error(self, error: str) -> None:
        if error:
            self.execution.output_error = error
        self.execution.status = Status.ERROR
        self.execution.end = timezone.now()
        self.execution.save(update_fields=["output_error", "status", "end"])
        self._on_task_end()

    def _on_completed(self, output: str) -> None:
        self.execution.status = Status.COMPLETED
        self.execution.end = timezone.now()
        if self.execution.configuration.tool.output_format and self.report.is_file():
            self.execution.output_file = self.report
        self.execution.output_plain = output
        self.execution.save(
            update_fields=["status", "end", "output_file", "output_plain"]
        )
        self._on_task_end()

    def execute(
        self,
        findings: List[Finding],
        target_ports: List[TargetPort],
        input_vulnerabilities: List[InputVulnerability],
        input_technologies: List[InputTechnology],
        wordlists: List[Wordlist],
    ) -> None:
        self._on_start()
        self.execution.configuration.tool.update_status()
        if not self.execution.configuration.tool.is_installed:
            message = f"[Tool] Tool {self.execution.configuration.tool.name} is not installed in the system. This execution has been skipped"
            logger.error(message)
            self._on_skip(message)
            return
        try:
            self.arguments = self._get_arguments(
                findings,
                target_ports,
                input_vulnerabilities,
                input_technologies,
                wordlists,
            )
        except RuntimeError as error:
            logger.error(f"[Tool] {str(error)}")
            self._on_skip(str(error))
            return
        environment = self._get_environment()
        self._before_running()
        try:
            output = "" if CONFIG.testing else self._run(environment)
        except (RuntimeError, Exception) as error:
            logger.error(
                f"[Tool] {self.execution.configuration.tool.name} execution finish with errors"
            )
            self._on_error(str(error))
            self._after_running()
            return
        self._after_running()
        self._on_completed(output)
        logger.info(
            f"[Tool] {self.execution.configuration.tool.name} execution has been completed"
        )

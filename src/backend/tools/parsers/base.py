import json
from typing import Any

import defusedxml.ElementTree as parser
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from django.db.models.query_utils import DeferredAttribute

from findings.framework.models import Finding
from tools.executors.base import BaseExecutor


class BaseParser:
    def __init__(self, executor: BaseExecutor, output: str | None = None) -> None:
        self.executor = executor
        self.output = output
        self.report = (
            executor.report
            if executor.report
            and executor.execution.configuration.tool.output_format
            and executor.report.is_file()
            and executor.report.stat().st_size > 0
            else None
        )
        self.findings: list[Finding] = []

    def create_finding(self, finding_type: type[Finding], **fields: Any) -> Finding:
        for (
            finding_type_used,
            finding_used,
        ) in self.executor.findings_used_in_execution.items():
            if (
                finding_type_used != finding_type
                and hasattr(finding_type, finding_type_used.__name__.lower())
                # Discard relations between findings
                and not isinstance(
                    getattr(finding_type, finding_type_used.__name__.lower()),
                    ReverseManyToOneDescriptor,
                )
                # Discard standard fields: Text, Number, etc.
                and not isinstance(
                    getattr(finding_type, finding_type_used.__name__.lower()),
                    DeferredAttribute,
                )
            ):
                fields[finding_type_used.__name__.lower()] = finding_used
        unique_finding = finding_type.objects.filter(
            **{
                **{f: fields.get(f) for f in finding_type.unique_fields},
                "executions__task__target": self.executor.execution.task.target,
            }
        )
        if unique_finding.exists():
            finding = unique_finding.first()
            for field, value in fields.items():
                setattr(finding, field, value)
            finding.save(update_fields=fields.keys())
        else:
            finding = finding_type.objects.create(**fields)
        finding.executions.add(self.executor.execution)
        self.findings.append(finding)
        return finding

    def _parse_report(self) -> None:
        pass

    def _parse_standard_output(self) -> None:
        pass

    def _load_report_as_json(
        self, default: dict[str, Any] | list[dict[str, Any]] = {}
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if self.report:
            with self.report.open("r", encoding="utf-8") as report:
                return json.load(report)
        return default

    def _load_report_as_xml(self) -> Any:
        return parser.parse(self.report).getroot()

    def _load_report_by_lines(self) -> list[str]:
        if self.report:
            with self.report.open("r", encoding="utf-8") as report:
                return report.readlines()
        return []

    def _protect_value(self, value: str | None) -> str | None:
        if not value:
            return value
        if self.executor.authentication:
            for sensitive_value in [
                self.executor.authentication.secret,
                self.executor.authentication.get_token(),
            ]:
                value = value.replace(sensitive_value, "*****")
        return value.replace(
            str(self.report),
            f"output.{self.executor.execution.configuration.tool.output_format}",
        ).strip()

    def _protect_execution(self) -> None:
        self.executor.execution.output_plain = self._protect_value(self.executor.execution.output_plain)
        self.executor.execution.output_error = self._protect_value(self.executor.execution.output_error)
        if self.report and self.report.is_file():
            with self.report.open("r") as read_report:
                data = read_report.read()
            with self.report.open("w") as write_report:
                write_report.write(self._protect_value(data))
        self.executor.execution.save(update_fields=["output_plain", "output_error"])

    def parse(self) -> None:
        if self.report:
            self._parse_report()
        elif self.output:
            self._parse_standard_output()
        self._protect_execution()

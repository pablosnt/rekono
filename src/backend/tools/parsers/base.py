import json
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

import defusedxml.ElementTree as parser
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from django.db.models.query_utils import DeferredAttribute

from findings.framework.models import Finding
from tools.executors.base import BaseExecutor


@dataclass
class BaseParser:
    executor: BaseExecutor
    output: str | None
    findings = []

    @cached_property
    def report(self) -> Path:
        return (
            self.executor.report
            if self.executor.report
            and self.executor.execution.configuration.tool.output_format
            and self.executor.report.is_file()
            and self.executor.report.stat().st_size > 0
            else None
        )

    def create_finding(self, finding_type: type[Finding], **fields: Any) -> Finding:
        for finding_type_used, finding_used in self.executor.findings_used_in_execution.items():
            if (
                finding_type_used != finding_type
                and hasattr(finding_type, finding_type_used.__name__.lower())
                # Discard relations between findings
                and not isinstance(
                    getattr(finding_type, finding_type_used.__name__.lower()), ReverseManyToOneDescriptor
                )
                # Discard standard fields: Text, Number, etc.
                and not isinstance(getattr(finding_type, finding_type_used.__name__.lower()), DeferredAttribute)
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

    def load_json_report(self) -> dict[str, Any] | list[dict[str, Any]] | None:
        if self.report:
            with self.report.open("r", encoding="utf-8") as report:
                return json.load(report)
        return None

    def load_xml_report(self) -> Any | None:
        try:
            return parser.parse(self.report).getroot()
        except Exception:
            return None

    def load_report_by_lines(self) -> list[str]:
        if self.report:
            with self.report.open("r", encoding="utf-8") as report:
                return report.readlines()
        return []

    def _protect_value(self, value: str | None) -> str | None:
        if not value:
            return value
        if self.executor.authentication:
            for sensitive_value in [self.executor.authentication.secret, self.executor.authentication.token]:
                value = value.replace(sensitive_value, "*****")
        return value.replace(
            str(self.report), f"output.{self.executor.execution.configuration.tool.output_format}"
        ).strip()

    def _protect_execution(self) -> None:
        self.executor.execution.output_plain = self._protect_value(self.executor.execution.output_plain)
        if self.report and self.report.is_file():
            with self.report.open("r") as read_report:
                data = read_report.read()
            with self.report.open("w") as write_report:
                write_report.write(self._protect_value(data))
        self.executor.execution.save(update_fields=["output_plain"])

    def _parse(self) -> None:
        pass

    def parse(self) -> None:
        self._parse()
        self._protect_execution()

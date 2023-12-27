import json
from typing import Any, Dict, List

import defusedxml.ElementTree as parser
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from django.db.models.query_utils import DeferredAttribute
from django.utils import timezone
from findings.framework.models import Finding
from tools.executors.base import BaseExecutor


class BaseParser:
    def __init__(self, executor: BaseExecutor, output: str = None) -> None:
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
        self.findings: List[Finding] = []

    def create_finding(self, finding_type: Finding, **fields: Any) -> Finding:
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

    def _load_report_as_json(self) -> Dict[str, Any]:
        with open(self.report, "r", encoding="utf-8") as report:
            return json.load(report)

    def _load_report_as_xml(self) -> Any:
        return parser.parse(self.report).getroot()

    def _load_report_by_lines(self) -> List[str]:
        with open(self.report, "r", encoding="utf-8") as report:
            return report.readlines()

    def parse(self) -> None:
        if self.report:
            self._parse_report()
        elif self.output:
            self._parse_standard_output()

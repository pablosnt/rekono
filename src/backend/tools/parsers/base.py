import json
import os
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
            and os.path.isfile(executor.report)
            and os.stat(executor.report).st_size > 0
            else None
        )
        self.findings: List[Finding] = []

    def create_finding(self, finding_type: Finding, **fields: Any) -> Finding:
        fields.update(
            {
                "target": self.executor.execution.task.target,
                "detected_by": self.executor.execution.configuration.tool,
                "last_seen": timezone.now(),
            }
        )
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
        unique_id = {}
        for field in finding_type.get_unique_fields():
            unique_id[field] = fields[field]
        finding, _ = finding_type.objects.update_or_create(**unique_id, defaults=fields)
        self.findings.append(finding)

    def _parse_report(self) -> None:
        pass

    def _parse_standard_output(self) -> None:
        pass

    def _load_report_as_json(self) -> Dict[str, Any]:
        with open(self.report, "r", encoding="utf-8") as report:
            return json.load(report)

    def _load_report_as_xml(self) -> Any:
        return parser.parse(self.path_output).getroot()

    def _load_report_by_lines(self) -> List[str]:
        with open(self.report, "r", encoding="utf-8") as report:
            return report.readlines()

    def parse(self) -> None:
        if self.report:
            self._parse_report()
        elif self.output:
            self._parse_standard_output()
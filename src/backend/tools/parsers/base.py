"""Base parser class for tool output processing and finding extraction.

Provides the base functionality for parsing tool outputs and extracting security
findings. All tool-specific parsers inherit from BaseParser and override the
_parse method to implement tool-specific parsing logic.
"""

import json
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

import defusedxml.ElementTree as parser
from backend.parameters.models import InputTechnology, InputVulnerability
from backend.target_ports.models import TargetPort
from backend.targets.models import Target
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from django.db.models.query_utils import DeferredAttribute

from findings.framework.models import Finding
from tools.executors.base import BaseExecutor


@dataclass
class BaseParser:
    """Base parser class for extracting security findings from tool outputs.

    Provides common functionality for parsing tool execution outputs and creating
    standardized finding objects. Handles multiple output formats including JSON,
    XML, and plain text, with automatic relationship management between findings
    and executions.

    Security Features:
        - Automatic sanitization of sensitive information in outputs
        - Secure XML parsing using defusedxml to prevent XXE attacks
        - Protection of authentication credentials in output data
        - Safe file handling with proper encoding support

    Attributes:
        executor (BaseExecutor): The executor instance that ran the tool
        output (str | None): Plain text output from tool execution
        findings (list): List of findings extracted during parsing

    Example:
        Create and use a parser:

        ```python
        parser = SomeToolParser(executor=executor, output=output)
        parser.parse()  # Extract findings from output
        findings = parser.findings  # Access extracted findings
        ```
    """

    executor: BaseExecutor
    output: str | None
    findings = []

    @cached_property
    def report(self) -> Path | None:
        """Get the valid report file path if available.

        Returns the executor's report file path only if it exists, has content,
        and the tool has a defined output format.

        Returns:
            Path | None: Valid report file path or None if not available
        """
        return (
            self.executor.report
            if self.executor.report
            and self.executor.execution.configuration.tool.output_format
            and self.executor.report.is_file()
            and self.executor.report.stat().st_size > 0
            else None
        )

    def is_finding_link_field(self, finding_type: type[Finding], field: str) -> bool:
        return (
            hasattr(finding_type, field)
            # Discard relations between findings (many-to-many, reverse foreign keys)
            and not isinstance(getattr(finding_type, field), ReverseManyToOneDescriptor)
            # Discard standard fields: Text, Number, etc. (these are not relationships)
            and not isinstance(getattr(finding_type, field), DeferredAttribute)
        )

    def create_finding(self, finding_type: type[Finding], linked_finding: bool = False, **fields: Any) -> Finding:
        """Create or update a finding with automatic relationship management.

        Creates a new finding or updates an existing one based on unique fields.
        Automatically establishes relationships with other findings from the same
        execution and associates the finding with the current execution.

        Args:
            finding_type (type[Finding]): The finding class to create
            **fields (Any): Field values for the finding

        Returns:
            Finding: The created or updated finding instance
        """
        # Automatically establish relationships with other findings from the same execution
        # This creates links between related findings (e.g., Host -> Port -> Path relationships)
        if not linked_finding:
            for finding_model, related_finding in self.executor.findings_used_in_execution.items():
                field = finding_model.__name__.lower()
                if finding_model != finding_type and self.is_finding_link_field(finding_type, field):
                    # Set the relationship field to link this finding with the related finding
                    fields[field] = related_finding
                    linked_finding = True
                    break
        if not linked_finding:
            port_for_input_parameter = None
            is_port_for_input_parameter = (
                InputVulnerability in self.executor.targets_used_in_execution
                or InputTechnology in self.executor.targets_used_in_execution
            )
            for related_target in [
                self.executor.targets_used_in_execution.get(TargetPort),
                TargetPort(target=self.executor.execution.task.target, port=self.executor.scanned_port)
                if self.executor.scanned_port is not None
                else None,
                self.executor.execution.task.target_port,
                self.executor.targets_used_in_execution.get(Target),
            ]:
                if not related_target:
                    continue
                field = related_target.input_type.model_class.__name__.lower()
                add_findings_to_field = self.is_finding_link_field(finding_type, field)
                if not fields.get(field) and (
                    (not is_port_for_input_parameter and add_findings_to_field)
                    or (is_port_for_input_parameter and field == "port")
                ):
                    related_finding = related_target.create_finding_from_user_input(self.executor.execution)
                    if add_findings_to_field:
                        fields[field] = related_finding
                        linked_finding = True
                    if is_port_for_input_parameter:
                        port_for_input_parameter = related_finding
                    break
            if is_port_for_input_parameter and port_for_input_parameter and not linked_finding:
                for input_parameter_class in [InputTechnology, InputVulnerability]:
                    field = input_parameter_class.input_type.model_class.__name__.lower()
                    if self.is_finding_link_field(finding_type, field):
                        fields[field] = self.executor.targets_used_in_execution.get(
                            input_parameter_class
                        ).create_finding_from_user_input(self.executor.execution, port=port_for_input_parameter)
                        linked_finding = True
                        break
        if linked_finding:
            fields["created_from_user_input"] = False
            finding = finding_type.objects.create(finding_type, self.executor.execution, **fields)
            self.findings.append(finding)
            return finding

    def load_json_report(self) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Load and parse JSON report file.

        Returns:
            dict[str, Any] | list[dict[str, Any]] | None: Parsed JSON data or None if no report
        """
        if self.report:
            with self.report.open("r", encoding="utf-8") as report:
                return json.load(report)

    def load_xml_report(self) -> Any | None:
        """Load and parse XML report file using secure XML parser.

        Uses defusedxml to safely parse XML content and prevent XXE attacks.

        Returns:
            Any | None: XML root element or None if parsing fails
        """
        try:
            return parser.parse(self.report).getroot()
        except Exception:
            return None

    def load_report_by_lines(self) -> list[str]:
        """Load report file content as list of lines.

        Returns:
            list[str]: List of lines from the report file or empty list if no report
        """
        if self.report:
            with self.report.open("r", encoding="utf-8") as report:
                return report.readlines()
        return []

    def _protect_value(self, value: str | None) -> str | None:
        """Sanitize sensitive information from output values.

        Replaces authentication credentials and file paths with sanitized values
        to prevent sensitive information exposure in stored outputs.

        Args:
            value (str | None): The value to sanitize

        Returns:
            str | None: Sanitized value with sensitive information removed
        """
        if not value:
            return value
        if self.executor.authentication:
            for sensitive_value in [self.executor.authentication.secret, self.executor.authentication.token]:
                value = value.replace(sensitive_value, "*****")
        return value.replace(
            str(self.report), f"output.{self.executor.execution.configuration.tool.output_format}"
        ).strip()

    def _protect_execution(self) -> None:
        """Sanitize sensitive information from execution outputs.

        Removes sensitive information from both plain text output and report files
        to prevent credential exposure in stored execution data.
        """
        self.executor.execution.output_plain = self._protect_value(self.executor.execution.output_plain)
        if self.report and self.report.is_file():
            with self.report.open("r") as read_report:
                data = read_report.read()
            with self.report.open("w") as write_report:
                write_report.write(self._protect_value(data))
        self.executor.execution.save(update_fields=["output_plain"])

    def _parse(self) -> None:
        """Parse tool output and extract findings.

        Override this method in tool-specific parser classes to implement
        custom parsing logic for extracting findings from tool outputs.
        """
        pass

    def parse(self) -> None:
        """Main parsing method that processes output and sanitizes sensitive information.

        Calls the tool-specific _parse method to extract findings, then sanitizes
        the execution output to remove sensitive information.
        """
        self._parse()
        self._protect_execution()

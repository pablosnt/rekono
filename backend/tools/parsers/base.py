"""Base parser class for tool output processing and finding extraction.

Provides the base functionality for parsing tool outputs and extracting security
findings. All tool-specific parsers inherit from BaseParser and override the
_parse method to implement tool-specific parsing logic.
"""

import json
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

import defusedxml.ElementTree as parser
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from django.db.models.query_utils import DeferredAttribute

from findings.framework.models import Finding
from findings.models import OSINT, Host
from parameters.models import InputTechnology, InputVulnerability
from rekono.settings import CONFIG
from target_ports.models import TargetPort
from targets.models import Target
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
    findings: list = field(default_factory=list)

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
        """Check if a field represents a valid finding relationship link.

        Determines whether a given field on a finding type represents a valid
        relationship that can be used for automatic finding linking, excluding
        reverse relationships and standard data fields.

        Args:
            finding_type (type[Finding]): The finding class to check
            field (str): The field name to validate

        Returns:
            bool: True if the field is a valid relationship link, False otherwise
        """
        return (
            hasattr(finding_type, field)
            # Discard relations between findings (many-to-many, reverse foreign keys)
            and not isinstance(getattr(finding_type, field), ReverseManyToOneDescriptor)
            # Discard standard fields: Text, Number, etc. (these are not relationships)
            and not isinstance(getattr(finding_type, field), DeferredAttribute)
        )

    def create_finding(
        self, finding_type: type[Finding], linked_finding: bool = False, **fields: Any
    ) -> Finding | None:
        """Create or update a finding with automatic relationship management.

        Creates a new finding or updates an existing one based on unique fields.
        Automatically establishes relationships with other findings from the same
        task and associates the finding with the current execution. Supports the
        creation of findings from data provided by users and ensures the integrity
        of the relationships between findings.

        Args:
            finding_type (type[Finding]): The finding class to create
            linked_finding (bool): Whether the finding has already been linked to other findings
            **fields (Any): Field values for the finding

        Returns:
            Finding | None: The created or updated finding instance, or None if creation fails
        """
        has_parent_findings = finding_type not in [OSINT, Host]
        if has_parent_findings:
            # Attempt to link with findings already discovered in this execution
            # This creates hierarchical relationships like Host > Port > Technology > Vulnerability > Exploit
            if not linked_finding:
                # Iterate through all findings that have been used as inputs in this execution
                for finding_model, related_finding in self.executor.findings_used_in_execution.items():
                    # Convert the finding model class name to lowercase to match field names
                    # Example: "Host" becomes "host" to match the foreign key field name
                    field = finding_model.__name__.lower()
                    # Check if this finding type can be linked to the current finding type
                    # Avoid self-references and ensure the field exists as a valid relationship
                    if finding_model != finding_type and self.is_finding_link_field(finding_type, field):
                        fields[field] = related_finding
                        linked_finding = True
                        # Stop after first successful link to avoid multiple relationships
                        break
            # If no existing findings to link with, try to create relationships from user inputs
            if not linked_finding:
                port_for_input_parameter = None
                # Check if we're dealing with input parameters that require port associations
                # Technologies and vulnerabilities often need to be associated with specific ports
                is_port_for_input_parameter = (
                    InputVulnerability in self.executor.targets_used_in_execution
                    or InputTechnology in self.executor.targets_used_in_execution
                )
                # Try to establish relationships with target-related inputs in priority order
                for related_target in [
                    # 1. First try explicit target port from execution context
                    self.executor.targets_used_in_execution.get(TargetPort),
                    # 2. Create target port from scanned port if available
                    TargetPort(target=self.executor.execution.task.target, port=self.executor.scanned_port)
                    if self.executor.scanned_port is not None
                    else None,
                    # 3. Use task's target port if specified
                    self.executor.execution.task.target_port,
                    # 4. Finally, try the base target
                    self.executor.targets_used_in_execution.get(Target),
                ]:
                    # Skip if no target is available at this level
                    if not related_target:
                        continue
                    # Determine the field name for this relationship type
                    # Example: Target -> "host", TargetPort -> "port"
                    field = related_target.input_type.model_class.__name__.lower()
                    add_findings_to_field = self.is_finding_link_field(finding_type, field)
                    # Check if we should create this relationship
                    if not fields.get(field) and (
                        # For regular findings, create if it's a valid link field
                        (not is_port_for_input_parameter and add_findings_to_field)
                        # For input parameters, specifically look for port relationships
                        or (is_port_for_input_parameter and field == "port")
                    ):
                        # Create a finding from the user input
                        related_finding = related_target.create_finding_from_user_input(self.executor.execution)
                        if not related_finding:
                            continue
                        # We avoid including the new user-input findings in the findings list
                        # to make parser unit tests easier and more intuitive
                        if not CONFIG.testing:  # pragma: no cover
                            self.findings.append(related_finding)
                        # Establish the relationship if it's a valid link field
                        if add_findings_to_field:
                            fields[field] = related_finding
                            linked_finding = True
                        # Store port finding for potential use with input parameters
                        if is_port_for_input_parameter:
                            port_for_input_parameter = related_finding
                        # Stop after first successful relationship
                        break
                # Handle special case for input parameters (Technologies/Vulnerabilities)
                # These need to be associated with ports when creating findings
                if is_port_for_input_parameter and port_for_input_parameter and not linked_finding:
                    # Process technology and vulnerability input parameters
                    for input_parameter_class in [InputVulnerability, InputTechnology]:
                        related_parameter = self.executor.targets_used_in_execution.get(input_parameter_class)
                        if not related_parameter:
                            continue
                        # Determine field name for the parameter type
                        # Example: InputTechnology -> "technology", InputVulnerability -> "vulnerability"
                        field = related_parameter.input_type.model_class.__name__.lower()
                        # Create finding from input parameter if it's a valid relationship
                        if self.is_finding_link_field(finding_type, field):
                            #  Create the parameter finding and associate it with the port
                            related_finding = related_parameter.create_finding_from_user_input(
                                self.executor.execution, port=port_for_input_parameter
                            )
                            if not related_finding:
                                continue
                            # We avoid including the new user-input findings in the findings list
                            # to make parser unit tests easier and more intuitive
                            if not CONFIG.testing:  # pragma: no cover
                                self.findings.append(related_finding)
                            fields[field] = related_finding
                            linked_finding = True
                            # Stop after first successful parameter association
                            break
            if not linked_finding and not CONFIG.testing:
                self.executor.logger.warning(
                    f"[{{self.executor.execution.configuration.tool.name}}] {finding_type.__name__} finding found during execution {self.executor.execution.id} is discarded because it has no parent finding to link to"
                )
                return
        # Create the finding if relationships were established or we're in testing mode,
        # as we need to test parsers completely
        # Mark as tool-generated (not from user input) since this is from parser output
        fields["created_from_user_input"] = False
        # Use the manager's create_finding method for proper duplicate handling
        finding = finding_type.objects.create_finding(self.executor.execution, **fields)
        # Add to the parser's findings list for tracking
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
        try:
            self._parse()
        finally:
            self._protect_execution()

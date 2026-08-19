"""Base parser that turns the output of a tool into findings.

The tool-specific parsers only implement how to read their output, since linking
each finding to the ones that it belongs to, and hiding the sensitive data of the
execution, are the same for all of them.
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
from security.cryptography import Crypto
from target_ports.models import TargetPort
from targets.models import Target
from tools.executors.base import BaseExecutor


@dataclass
class BaseParser:
    """Findings discovered by one execution, read from the output of its tool.

    Attributes:
        executor: Executor that ran the tool, which knows what it scanned.
        output: Text that the tool wrote to the standard output.
        findings: Findings discovered so far.
        user_input_findings: Findings created from the target of the execution,
          reused by all the findings that need the same parent.
    """

    executor: BaseExecutor
    output: str | None
    findings: list = field(default_factory=list)
    user_input_findings: dict = field(default_factory=dict)

    @cached_property
    def report(self) -> Path | None:
        """The report file of the execution, or None if the tool wrote no report."""
        return (
            self.executor.report
            if self.executor.report
            and self.executor.execution.configuration.tool.output_format
            and self.executor.report.is_file()
            and self.executor.report.stat().st_size > 0
            else None
        )

    def create_user_input_finding(self, related_target: Any) -> Any | None:
        """Get the finding that represents the target that the execution scanned.

        Args:
            related_target: Target or target port to create the finding from.

        Returns:
            The finding, or None if it couldn't be created.
        """
        # The findings of one execution share the same parent, so it's created only once: the
        # deduplication query, the lock of the target, and the DNS resolution of its domain are
        # expensive enough to matter when a tool reports hundreds of findings
        key = Crypto.hash("-".join([related_target.__class__.__name__, str(related_target.pk)]))
        if key not in self.user_input_findings:
            finding = related_target.create_finding_from_user_input(self.executor.execution)
            # A failure isn't remembered, so the next finding can try again
            if finding is None:
                return None
            self.user_input_findings[key] = finding
        return self.user_input_findings[key]

    def is_finding_link_field(self, finding_type: type[Finding], field: str) -> bool:
        """Check if a finding type can be linked to another one by a field.

        Args:
            finding_type: Kind of finding whose fields are inspected.
            field: Name of the field that would hold the link.

        Returns:
            Whether that field is a link to a single parent finding, and not a
            plain value or a collection of related findings.
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
        """Create a finding and link it to the one that it was discovered from.

        Args:
            finding_type: Kind of finding to create.
            linked_finding: Whether the caller already linked the finding, which
              only the parsers that know the relation themselves can do.
            **fields: Data of the finding.

        Returns:
            The created finding, or None if it's discarded because there is nothing
            to link it to, since a finding without a parent can't be placed
            anywhere in the target.
        """
        has_parent_findings = finding_type not in [OSINT, Host]
        if has_parent_findings:
            # The findings used as input for this execution are the closest parents that a new
            # finding can have, so they are the first option
            if not linked_finding:
                for finding_model, related_finding in self.executor.findings_used_in_execution.items():
                    field = finding_model.__name__.lower()
                    if finding_model != finding_type and self.is_finding_link_field(finding_type, field):
                        fields[field] = related_finding
                        linked_finding = True
                        break
            # Without input findings, the parent is created from what the execution scanned,
            # searched from the most specific place to the least one
            if not linked_finding:
                port_for_input_parameter = None
                # The technologies and the vulnerabilities that the users provide are always
                # placed in a port, so the port is what has to be created for them
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
                        related_finding = self.create_user_input_finding(related_target)
                        if not related_finding:
                            continue
                        # We avoid including the new user-input findings in the findings list
                        # to make parser unit tests easier and more intuitive
                        if not CONFIG.testing:  # pragma: no cover
                            self.findings.append(related_finding)
                        if add_findings_to_field:
                            fields[field] = related_finding
                            linked_finding = True
                        if is_port_for_input_parameter:
                            port_for_input_parameter = related_finding
                        break
                # The finding is placed in the technology or in the vulnerability that the users
                # provided, which is created in the port that was just created for it
                if is_port_for_input_parameter and port_for_input_parameter and not linked_finding:
                    for input_parameter_class in [InputVulnerability, InputTechnology]:
                        related_parameter = self.executor.targets_used_in_execution.get(input_parameter_class)
                        if not related_parameter:
                            continue
                        field = related_parameter.input_type.model_class.__name__.lower()
                        if self.is_finding_link_field(finding_type, field):
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
                            break
            # The tests create the findings without a parent, so the parsers can be tested
            # without having to build the whole target around them
            if not linked_finding and not CONFIG.testing:
                self.executor.logger.warning(
                    f"[{self.executor.execution.configuration.tool.name}] {finding_type.__name__} finding found during execution {self.executor.execution.id} is discarded because it has no parent finding to link to"
                )
                return
        fields["created_from_user_input"] = False
        finding = finding_type.objects.create_finding(self.executor.execution, **fields)
        self.findings.append(finding)
        return finding

    def load_json_report(self) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Read the report of the execution as JSON.

        Returns:
            The report content, or None if there is no report or if the tool wrote
            something that isn't valid JSON, which happens when it fails.
        """
        if self.report:
            with self.report.open("r", encoding="utf-8") as report:
                try:
                    return json.load(report)
                except json.JSONDecodeError:
                    return None

    def load_xml_report(self) -> Any | None:
        """Read the report of the execution as XML.

        Returns:
            The root element of the report, or None if there is no report or if the
            tool wrote something that isn't valid XML, which happens when it fails.
        """
        # defusedxml is used instead of the standard library to avoid XXE attacks from the
        # reports, whose content comes from the scanned targets
        try:
            return parser.parse(self.report).getroot()
        except Exception:
            return None

    def load_report_by_lines(self) -> list[str]:
        """Read the report of the execution as a list of lines.

        Returns:
            The lines of the report, or an empty list if there is no report.
        """
        if self.report:
            with self.report.open("r", encoding="utf-8") as report:
                return report.readlines()
        return []

    def mask_sensitive_data(self, value: str | None) -> str | None:
        """Remove the authentication secrets and the Rekono paths from a text.

        Args:
            value: Text written by the tool, which may quote the credentials that
              it received, the path of its own report, or the ones of the
              wordlists that it enumerated with.

        Returns:
            The text with the credentials masked, the report path replaced by a
            generic output name, and the Rekono directories removed from the rest
            of the paths, or the text unchanged when it's empty.
        """
        if not value:
            return value
        if self.report:
            value = value.replace(
                str(self.report), f"output.{self.executor.execution.configuration.tool.output_format}"
            )
        return self.executor.mask_sensitive_data(value).strip()

    def _parse(self) -> None:
        """Read the output of the tool and create the findings that it reports.

        An implementation that iterates over several items must catch and log the
        errors of each one, because parse() catches the exceptions of the whole
        method, so a failure in the middle of a loop drops the rest of the findings.
        """
        pass

    def parse(self) -> None:
        """Create the findings of the execution and hide its sensitive data.

        A parsing failure is logged instead of being propagated, so the findings
        created before it are kept and the execution isn't marked as failed. The
        rest of the report is not parsed though, so every finding that the tool
        reported after the failing one is lost without any sign in the execution.
        """
        try:
            self._parse()
        except Exception as ex:
            self.executor.logger.exception(
                f"[{self.executor.execution.configuration.tool.name}] {ex.__class__.__name__} error while parsing the output of execution {self.executor.execution.id}: {str(ex)}"
            )
        finally:
            self.executor.execution.output_plain = self.mask_sensitive_data(self.executor.execution.output_plain)
            if self.report and self.report.is_file():
                with self.report.open("r") as read_report:
                    data = read_report.read()
                with self.report.open("w") as write_report:
                    write_report.write(self.mask_sensitive_data(data))
            self.executor.execution.save(update_fields=["output_plain"])

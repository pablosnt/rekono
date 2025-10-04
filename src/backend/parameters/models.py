"""Django models for input parameters in security tool execution.

This module provides the concrete implementation of input parameter models used
in security testing workflows. Input parameters serve as configurable data inputs
for security tools and can be associated with tasks to provide context-specific
testing parameters. The system supports technology specifications and vulnerability
references with validation and parsing capabilities.

Architecture:
    Both parameter types extend the InputParameter base model and implement specific
    field configurations, validation rules, and parsing mappings for integration with
    security testing tools. The models include filtering capabilities and deduplication
    logic to ensure data consistency and efficient parameter management.
"""

from typing import Any

from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from parameters.framework.models import InputParameter
from security.validators.input_validator import Regex, Validator


class InputTechnology(InputParameter):
    """Model representing technology parameters for security tool execution.

    Represents software and hardware technology specifications that serve as input
    parameters for security testing tools. Technology parameters include name and
    version information and are used for targeted security assessments, compatibility
    testing, and technology-specific vulnerability scanning workflows.

    Attributes:
        name (TextField): Technology name with injection prevention validation (max 100 chars)
        version (TextField): Optional technology version with validation (max 100 chars)

    Example:
        Create a technology parameter for Apache web server:

        ```python
        tech_param = InputTechnology.objects.create(
            name="Apache",
            version="2.4.41"
        )
        # Associate with a task for project context
        task.input_technologies.add(tech_param)
        ```
    """

    name = models.TextField(max_length=100, validators=[Validator(Regex.NAME, code="name", deny_injections=True)])
    version = models.TextField(
        max_length=100, validators=[Validator(Regex.NAME, code="version", deny_injections=True)], blank=True, null=True
    )

    _filters = [BaseInput.Filter(type=str, field="name", contains=True)]
    _parse_mapping = {InputKeyword.TECHNOLOGY: "name", InputKeyword.VERSION: "version"}

    def __str__(self) -> str:
        """Return string representation of the technology parameter.

        Returns:
            str: Technology name with version if available, otherwise just the name
        """
        return f"{self.name} - {self.version}" if self.version else self.name

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        """Create a Technology finding from user input technology parameter.

        Creates a Technology finding associated with a port when user input
        technology parameters are used in execution context.

        Args:
            execution (Any): The execution context for the finding
            **fields (Any): Additional fields including port information

        Returns:
            Any | None: Created Technology finding or None if no port specified
        """
        from findings.models import Technology

        if "port" in fields:
            return Technology.objects.create_finding(
                Technology,
                execution,
                **{**fields, "name": self.name, "version": self.version, "created_from_user_input": True},
            )


class InputVulnerability(InputParameter):
    """Model representing vulnerability parameters for security tool execution.

    Represents vulnerability references and CVE identifiers that serve as input
    parameters for focused security testing workflows. Vulnerability parameters
    enable targeted exploit verification, proof-of-concept testing, and
    vulnerability-specific security assessments.

    Attributes:
        cve (TextField): CVE identifier with format validation and injection prevention (max 20 chars)

    Example:
        Create a vulnerability parameter for a specific CVE:

        ```python
        vuln_param = InputVulnerability.objects.create(
            cve="CVE-2021-44228"
        )
        # Associate with a task for focused vulnerability testing
        task.input_vulnerabilities.add(vuln_param)
        ```
    """

    cve = models.TextField(max_length=20, validators=[Validator(Regex.CVE, code="cve", deny_injections=True)])

    _filters = [
        BaseInput.Filter(type=str, field="cve", processor=lambda v: "cve"),
        BaseInput.Filter(type=str, field="cve", processor=lambda v: v.lower()),
    ]
    _parse_mapping = {InputKeyword.CVE: "cve"}

    def __str__(self) -> str:
        """Return string representation of the vulnerability parameter.

        Returns:
            str: The CVE identifier
        """
        return self.cve

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        """Create a Vulnerability finding from user input vulnerability parameter.

        Creates a Vulnerability finding associated with a port when user input
        vulnerability parameters are used in execution context.

        Args:
            execution (Any): The execution context for the finding
            **fields (Any): Additional fields including port information

        Returns:
            Any | None: Created Vulnerability finding or None if no port specified
        """
        from findings.models import Vulnerability

        if "port" in fields:
            return Vulnerability.objects.create_finding(
                Vulnerability,
                execution,
                **{**fields, "name": self.cve, "cve": self.cve, "created_from_user_input": True},
            )

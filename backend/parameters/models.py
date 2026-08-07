"""Models of the data that the users provide as input for the tools.

Both parameters can also become findings, so the tools that only work from findings
can be executed against the data that the users provide.
"""

from typing import Any

from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from parameters.framework.models import InputParameter
from security.validators.input_validator import Regex, Validator


class InputTechnology(InputParameter):
    """Technology that the users know that a target runs.

    Attributes:
        name: Name of the technology.
        version: Version of the technology, which is often unknown.
    """

    name = models.TextField(max_length=100, validators=[Validator(Regex.NAME, code="name", deny_injections=True)])
    version = models.TextField(
        max_length=100, validators=[Validator(Regex.NAME, code="version", deny_injections=True)], blank=True, null=True
    )

    _filters = [BaseInput.Filter(type=str, field="name", contains=True)]
    # Version is parsed as empty string when None, as most of the tools working from technologies only require the technology name
    _parse_mapping = {
        InputKeyword.TECHNOLOGY: "name",
        InputKeyword.VERSION: lambda instance, task: instance.version or "",
    }

    def __str__(self) -> str:
        """Return the technology name, with its version if it's known."""
        return f"{self.name} - {self.version}" if self.version else self.name

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        """Create a technology finding from this parameter.

        Args:
            execution: Execution that the created finding belongs to.
            **fields: Extra values for the finding, whose ``port`` is required
              because a technology is always found on one.

        Returns:
            The created finding, or None if the port where the technology runs is
            unknown, since a technology finding without a port can't be scanned.
        """
        from findings.models import Technology

        if "port" in fields:
            return Technology.objects.create_finding(
                execution, **{**fields, "name": self.name, "version": self.version, "created_from_user_input": True}
            )


class InputVulnerability(InputParameter):
    """Vulnerability that the users want to check in a target.

    Attributes:
        cve: CVE identifier of the vulnerability.
    """

    cve = models.TextField(max_length=20, validators=[Validator(Regex.CVE, code="cve", deny_injections=True)])

    _filters = [BaseInput.Filter(type=str, field="cve", contains=True, processor=lambda v: v.lower())]
    _parse_mapping = {InputKeyword.CVE: "cve"}

    def __str__(self) -> str:
        """Return the CVE identifier of the vulnerability."""
        return self.cve

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        """Create a vulnerability finding from this parameter.

        Args:
            execution: Execution that the created finding belongs to.
            **fields: Extra values for the finding, whose ``port`` is required
              because a vulnerability is always expected on one.

        Returns:
            The created finding, or None if the port where the vulnerability is
            expected is unknown, since a vulnerability without a port can't be
            scanned.
        """
        from findings.models import Vulnerability

        if "port" in fields:
            return Vulnerability.objects.create_finding(
                execution, **{**fields, "name": self.cve, "cve": self.cve, "created_from_user_input": True}
            )

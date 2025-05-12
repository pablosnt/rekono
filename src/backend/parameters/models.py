from typing import Any

from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from parameters.framework.models import InputParameter
from security.validators.input_validator import Regex, Validator

# Create your models here.


class InputTechnology(InputParameter):
    """Input technology model."""

    name = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name", deny_injections=True)],
    )
    version = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="version", deny_injections=True)],
        blank=True,
        null=True,
    )

    filters = [BaseInput.Filter(type=str, field="name", contains=True)]
    parse_mapping = {InputKeyword.TECHNOLOGY: "name", InputKeyword.VERSION: "version"}

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return f"{self.name} - {self.version}" if self.version else self.name


class InputVulnerability(InputParameter):
    """Input vulnerability model."""

    cve = models.TextField(
        max_length=20,
        validators=[Validator(Regex.CVE.value, code="cve", deny_injections=True)],
    )

    filters = [
        BaseInput.Filter(type=str, field="cve", processor=lambda v: "cve"),
        BaseInput.Filter(type=str, field="cve", processor=lambda v: v.lower()),
    ]
    parse_mapping = {InputKeyword.CVE: "cve"}

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.cve

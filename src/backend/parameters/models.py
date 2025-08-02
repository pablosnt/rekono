from django.db import models

from framework.enums import InputKeyword
from framework.models import BaseInput
from parameters.framework.models import InputParameter
from security.validators.input_validator import Regex, Validator


class InputTechnology(InputParameter):
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

    _filters = [BaseInput.Filter(type=str, field="name", contains=True)]
    _parse_mapping = {InputKeyword.TECHNOLOGY: "name", InputKeyword.VERSION: "version"}

    def __str__(self) -> str:
        return f"{self.name} - {self.version}" if self.version else self.name


class InputVulnerability(InputParameter):
    cve = models.TextField(
        max_length=20,
        validators=[Validator(Regex.CVE.value, code="cve", deny_injections=True)],
    )

    _filters = [
        BaseInput.Filter(type=str, field="cve", processor=lambda v: "cve"),
        BaseInput.Filter(type=str, field="cve", processor=lambda v: v.lower()),
    ]
    _parse_mapping = {InputKeyword.CVE: "cve"}

    def __str__(self) -> str:
        return self.cve

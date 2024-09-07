from typing import Any

from django.db import models
from framework.enums import InputKeyword
from framework.models import BaseInput
from rekono.settings import AUTH_USER_MODEL
from security.validators.input_validator import Regex, Validator
from targets.models import Target

# Create your models here.


class HttpHeader(BaseInput):
    target = models.ForeignKey(
        Target,
        related_name="http_headers",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="http_headers",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    key = models.TextField(
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="key", deny_injections=True)],
    )
    value = models.TextField(
        max_length=500,
        validators=[Validator(Regex.TEXT.value, code="value", deny_injections=True)],
    )

    filters = [BaseInput.Filter(type=str, field="key")]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                "key",
                name="unique_http_headers",
                condition=models.Q(user__isnull=True, target__isnull=True),
            ),
            models.UniqueConstraint(
                "user",
                "key",
                name="unique_http_headers_2",
                condition=models.Q(target__isnull=True),
            ),
            models.UniqueConstraint(
                "target",
                "key",
                name="unique_http_headers_3",
                condition=models.Q(user__isnull=True),
            ),
        ]

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        return {
            InputKeyword.HEADERS.name.lower(): {
                **accumulated.get(InputKeyword.HEADERS.name.lower(), {}),
                self.key: self.value,
            }
        }

    def __str__(self) -> str:
        parent = self.target or self.user
        return f"{parent.__str__()} - {self.key}" if parent else self.key

    @classmethod
    def get_project_field(cls) -> str:
        return "target__project"

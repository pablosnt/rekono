from functools import cached_property
from typing import Any, Callable, cast

import requests
import urllib3
from django.db import models
from django.db.models import Q

from framework.enums import InputKeyword
from rekono.settings import AUTH_USER_MODEL, CONFIG
from security.cryptography.encryption import Encryptor


class BaseModel(models.Model):
    _project_field = ""

    class Meta:
        abstract = True

    @cached_property
    def parent_project(self) -> Any | list[Any] | None:
        filter_field = self.__class__._project_field
        if filter_field:
            project = self
            for field in filter_field.split("__"):
                if hasattr(project, field) and getattr(project, field):
                    project = getattr(project, field)
                else:
                    return None
            return project
        return None

    def __str__(self) -> str:
        return self.__class__.__name__


class BaseEncrypted(BaseModel):
    class Meta:
        abstract = True

    _encryptor = Encryptor(CONFIG.encryption_key) if CONFIG.encryption_key else None
    _encrypted_field = "_secret"

    @property
    def secret(self) -> str | None:
        return (
            (
                self._encryptor.decrypt(getattr(self, self._encrypted_field))
                if self._encryptor
                else getattr(self, self._encrypted_field)
            )
            if hasattr(self, self._encrypted_field) and getattr(self, self._encrypted_field)
            else None
        )

    @secret.setter
    def secret(self, value: str) -> None:
        if hasattr(self, self._encrypted_field):
            setattr(
                self,
                self._encrypted_field,
                (self._encryptor.encrypt(value) if self._encryptor and value is not None else value),
            )


class BaseInput(BaseModel):
    class Meta:
        abstract = True

    class Filter:
        def __init__(
            self,
            type: type,
            field: str,
            contains: bool = False,
            processor: Callable | None = None,
        ) -> None:
            self.type = type
            self.field = field
            self.contains = contains
            self.processor = processor

        def filter(self, condition: str, value: Any, is_negative: bool = False) -> bool:
            if self.processor:
                value = self.processor(value)
            try:
                return (
                    issubclass(self.type, models.TextChoices)
                    and self._compare(condition.upper(), cast(models.TextChoices, filter.type)(value).name, is_negative)
                ) or (
                    filter.type in [str, int]
                    and self._compare(
                        str(condition).strip().lower(), str(value).strip().lower(), is_negative, self.contains
                    )
                )
            except (ValueError, KeyError):
                return False

        def _compare(self, filter: Any, value: Any, negative: bool = False, contains: bool = False) -> bool:
            return self._assert(filter, value, contains) if not negative else not self._assert(filter, value, contains)

        def _assert(self, filter: str, value: str, contains: bool) -> bool:
            return filter == value if not contains else filter in value

    _filters: list[Filter] = []
    _parse_mapping: dict[InputKeyword, str | Callable | dict[str, str]] = {}
    _parse_dependencies: list[str] = []

    @cached_property
    def input_type(self) -> Any:
        from input_types.models import InputType

        reference = f"{self._meta.app_label}.{self._meta.model_name}"
        return InputType.objects.filter(Q(model=reference) | Q(fallback_model=reference)).first()

    def clean_path(self, value: str | None) -> str | None:
        return f"/{value}" if value and len(value) > 1 and value[0] != "/" else value

    def get_url(
        self,
        host: str,
        port: int | None = None,
        endpoint: str | None = None,
        protocols: list[str] = ["http", "https"],
    ) -> str | None:
        urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
        if endpoint is None:
            endpoint = ""
        elif endpoint.startswith("/"):
            endpoint = endpoint[1:]
        schema = "{protocol}://{host}/{endpoint}"
        if port:
            schema = "{protocol}://{host}:{port}/{endpoint}"  # Include port schema if port exists
            if port == 80:
                protocols = ["http"]
            elif port == 443:
                protocols = ["https"]
        for protocol in protocols:  # For each protocol
            url_to_test = schema.format(protocol=protocol, host=host, port=port, endpoint=endpoint)
            try:
                # nosemgrep: python.requests.security.disabled-cert-validation.disabled-cert-validation
                requests.get(url_to_test, timeout=5, verify=False)
                return url_to_test
            except Exception:
                continue
        return None

    def filter(self, argument_input: Any, target: Any = None) -> bool:
        if not argument_input.filter:
            return True
        if " or " in argument_input.filter:
            operator = " or "
            is_or = True
        else:
            operator = " and "
            is_or = False
        conclusion = True
        for condition in argument_input.filter.split(operator):
            is_negative = condition.startswith("!")
            if is_negative:
                condition = condition[1:]
            filter_conclusion = False
            for filter in self._filters:
                _conclusion = filter.filter(condition, getattr(self, filter.field), is_negative)
                if _conclusion:
                    if is_or:
                        return True
                    else:
                        filter_conclusion = True
                        break
            conclusion = conclusion and filter_conclusion
        return conclusion

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        result = {}
        for dependency in self._parse_dependencies:
            if (
                hasattr(self, dependency)
                and getattr(self, dependency)
                and isinstance(getattr(self, dependency), BaseInput)
            ):
                result.update(getattr(self, dependency).parse(accumulated))
        for keyword, field_or_function in self._parse_mapping.items():
            value = (
                getattr(self, field_or_function)
                if isinstance(field_or_function, str) and hasattr(self, field_or_function)
                else (field_or_function(self) if isinstance(field_or_function, Callable) else field_or_function)
            )
            if value is None:
                value = ""
            key = keyword.name.lower()
            current_value = accumulated.get(key)
            if current_value is not None:
                if isinstance(current_value, list):
                    result[key] = accumulated.get(key, []) + (value if isinstance(value, list) else [value])
                    continue
                elif isinstance(current_value, dict) and isinstance(value, dict):
                    result[key] = {**accumulated.get(key, {}), **value}
                    continue
            result[key] = value
        return result


class BaseLike(BaseModel):
    liked_by = models.ManyToManyField(AUTH_USER_MODEL, related_name="liked_%(class)s")

    class Meta:
        abstract = True

import importlib
from typing import Any, Callable, cast

import requests
import urllib3
from django.db import models
from django.db.models import Q

from framework.enums import InputKeyword
from rekono.settings import AUTH_USER_MODEL, CONFIG
from security.cryptography.encryption import Encryptor


class BaseModel(models.Model):
    project_field = ""

    class Meta:
        abstract = True

    def get_project(self) -> Any | list[Any]:
        filter_field = self.__class__.project_field
        if filter_field:
            project = self
            for field in filter_field.split("__"):
                if hasattr(project, field) and getattr(project, field):
                    project = getattr(project, field)
                else:
                    return None
            return project
        return None

    def _get_related_class(self, package: str, name: str) -> Any:
        try:
            # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
            module = importlib.import_module(f"{package.lower()}.{name.lower().replace(' ', '_').replace('-', '_')}")
            cls = getattr(
                module,
                name[0].upper() + name[1:].lower().replace(" ", "").replace("-", ""),
            )
        except (AttributeError, ModuleNotFoundError):
            # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
            module = importlib.import_module(f"{package}.base")
            type = package.split(".")[-1][:-1]
            cls = getattr(module, f"Base{type[0].upper() + type[1:].lower()}")
        return cls

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
    """Class to be extended by all the objects that can be used in tool executions as argument."""

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

    filters: list[Filter] = []
    parse_mapping: dict[InputKeyword, str | Callable | dict[str, str]] = {}
    parse_dependencies: list[str] = []

    def _clean_path(self, value: str) -> str:
        return f"/{value}" if len(value) > 1 and value[0] != "/" else value

    def _get_url(
        self,
        host: str,
        port: int | None = None,
        endpoint: str = "",
        protocols: list[str] = ["http", "https"],
    ) -> str | None:
        """Get a HTTP or HTTPS URL from host, port and endpoint.

        Args:
            host (str): Host to include in the URL
            port (int, optional): Port to include in the URL. Defaults to None.
            endpoint (str, optional): Endpoint to include in the URL. Defaults to ''.
            protocols (list[str], optional): Protocol list to check. Defaults to ['http', 'https'].

        Returns:
            str | None: [description]
        """
        urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
        if endpoint.startswith("/"):
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
                requests.get(url_to_test, timeout=5, verify=False)  # nosec
                return url_to_test
            except Exception:  # nosec
                continue
        return None

    def _compare(self, filter: str, value: str, contains: bool) -> bool:
        return filter == value if not contains else filter in value

    def _compare_filter(self, filter: Any, value: Any, negative: bool = False, contains: bool = False) -> bool:
        return self._compare(filter, value, contains) if not negative else not self._compare(filter, value, contains)

    def filter(self, argument_input: Any, target: Any = None) -> bool:
        """Check if this instance is valid based on input filter.

        Args:
            input (any): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        """
        if not argument_input.filter:
            return True
        filter_value = argument_input.filter
        for split, or_condition in [(" or ", True), (" and ", False)]:
            if split not in filter_value and or_condition:
                continue
            for match_value in filter_value.split(split):
                negative = match_value.startswith("!")
                if negative:
                    match_value = match_value[1:]
                for filter in self.filters:
                    and_condition = False
                    field_value = getattr(self, filter.field)
                    if filter.processor:
                        field_value = filter.processor(field_value)
                    try:
                        if (
                            issubclass(filter.type, models.TextChoices)
                            and self._compare_filter(
                                cast(models.TextChoices, filter.type)[match_value.upper()],
                                field_value,
                                negative,
                            )
                        ) or (
                            hasattr(self, match_value)
                            and self._compare_filter(
                                filter.type(getattr(self, match_value)),
                                field_value,
                                negative,
                                filter.contains,
                            )
                        ):
                            if or_condition:
                                return True
                            else:
                                and_condition = True
                        elif not or_condition:
                            return False
                    except (ValueError, KeyError):
                        continue
                    if not or_condition and and_condition:
                        return True
        return False

    def parse(self, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        result = {}
        for dependency in self.parse_dependencies:
            if (
                hasattr(self, dependency)
                and getattr(self, dependency)
                and isinstance(getattr(self, dependency), BaseInput)
            ):
                result.update(getattr(self, dependency).parse(accumulated))
        for keyword, map in self.parse_mapping.items():
            value = (
                getattr(self, map)
                if isinstance(map, str) and hasattr(self, map)
                else (map(self) if isinstance(map, Callable) else map)
            )
            if value is None:
                continue
            key = keyword.name.lower()
            current_value = accumulated.get(key)
            if current_value is not None:
                if isinstance(current_value, list):
                    result[key] = accumulated.get(key, []) + (value if isinstance(value, list) else [value])
                    continue
                elif isinstance(current_value, dict):
                    result[key] = {**accumulated.get(key, {}), **value}
                    continue
            result[key] = value
        return result

    def get_input_type(self) -> Any:
        from input_types.models import InputType

        reference = f"{self._meta.app_label}.{self._meta.model_name}"
        return InputType.objects.filter(Q(model=reference) | Q(fallback_model=reference)).first()


class BaseLike(BaseModel):
    """Common and abstract LikeBase model, to define common fields for all models that user can like."""

    liked_by = models.ManyToManyField(AUTH_USER_MODEL, related_name="liked_%(class)s")

    class Meta:
        abstract = True

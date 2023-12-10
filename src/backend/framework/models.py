import importlib
from typing import Any, Dict, List, Optional

import requests
import urllib3
from django.db import models
from django.db.models import Q
from rekono.settings import AUTH_USER_MODEL, CONFIG
from security.cryptography.encryption import Encryptor


class BaseModel(models.Model):
    class Meta:
        abstract = True

    def get_project(self) -> Any:
        filter_field = self.__class__.get_project_field()
        if filter_field:
            project = self
            for field in filter_field.split("__"):
                if hasattr(project, field):
                    project = getattr(project, field)
                else:  # pragma: no cover
                    return None
            return project

    @classmethod
    def get_project_field(cls) -> str:
        return None

    def _get_related_class(self, package: str, name: str) -> Any:
        try:
            # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
            module = importlib.import_module(
                f'{package.lower()}.{name.lower().replace(" ", "_").replace("-", "_")}'
            )
            cls = getattr(
                module,
                name[0].upper() + name[1:].lower().replace(" ", "").replace("-", ""),
            )
        except (AttributeError, ModuleNotFoundError) as ex:
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
    def secret(self) -> str:
        return (
            (
                self._encryptor.decrypt(getattr(self, self._encrypted_field))
                if self._encryptor
                else getattr(self, self._encrypted_field)
            )
            if hasattr(self, self._encrypted_field)
            and getattr(self, self._encrypted_field)
            else None
        )

    @secret.setter
    def secret(self, value: str) -> None:
        if hasattr(self, self._encrypted_field):
            setattr(
                self,
                self._encrypted_field,
                self._encryptor.encrypt(value)
                if self._encryptor and value is not None
                else value,
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
            processor: callable = None,
        ) -> None:
            self.type = type
            self.field = field
            self.contains = contains
            self.processor = processor

    filters: List[Filter] = []

    def _clean_path(self, value: str) -> str:
        return f"/{value}" if len(value) > 1 and value[0] != "/" else value

    def _get_url(
        self,
        host: str,
        port: int = None,
        endpoint: str = "",
        protocols: List[str] = ["http", "https"],
    ) -> Optional[str]:
        """Get a HTTP or HTTPS URL from host, port and endpoint.

        Args:
            host (str): Host to include in the URL
            port (int, optional): Port to include in the URL. Defaults to None.
            endpoint (str, optional): Endpoint to include in the URL. Defaults to ''.
            protocols (List[str], optional): Protocol list to check. Defaults to ['http', 'https'].

        Returns:
            Optional[str]: [description]
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
            url_to_test = schema.format(
                protocol=protocol, host=host, port=port, endpoint=endpoint
            )
            try:
                # nosemgrep: python.requests.security.disabled-cert-validation.disabled-cert-validation
                requests.get(url_to_test, timeout=5, verify=False)
                return url_to_test
            except:
                continue
        return None

    def _compare_filter(
        self, filter: Any, value: Any, negative: bool = False, contains: bool = False
    ) -> bool:
        comparison = lambda f, v: f == v if not contains else f in v
        return (
            comparison(filter, value) if not negative else not comparison(filter, value)
        )

    def filter(self, input: Any, target: Any = None) -> bool:
        """Check if this instance is valid based on input filter.

        Args:
            input (Any): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        """
        if not input.filter:
            return True
        for filter_value in input.filter.split(" or "):
            negative = filter_value.startswith("!")
            if negative:
                filter_value = filter_value[1:]
            for filter in self.filters:
                field_value = getattr(self, filter.field)
                if filter.processor:
                    field_value = filter.processor(field_value)
                try:
                    if (
                        issubclass(filter.type, models.TextChoices)
                        and self._compare_filter(
                            filter.type[filter_value.upper()], field_value, negative
                        )
                    ) or (
                        hasattr(self, filter_value)
                        and self._compare_filter(
                            filter.type(getattr(self, filter_value)),
                            field_value,
                            negative,
                            filter.contains,
                        )
                    ):
                        return True
                except (ValueError, KeyError):
                    pass
        return False

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Get useful information from this instance to be used in tool execution as argument.

        To be implemented by subclasses.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        """
        return {}  # pragma: no cover

    def get_input_type(self) -> Any:
        from input_types.models import InputType

        reference = f"{self._meta.app_label}.{self._meta.model_name}"
        return InputType.objects.filter(
            Q(model=reference) | Q(fallback_model=reference)
        ).first()


class BaseLike(BaseModel):
    """Common and abstract LikeBase model, to define common fields for all models that user can like."""

    liked_by = models.ManyToManyField(AUTH_USER_MODEL, related_name="liked_%(class)s")

    class Meta:
        abstract = True

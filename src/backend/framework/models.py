from typing import Any, Dict, List, Optional

import requests
import urllib3
from django.db import models


class BaseInput(models.Model):
    """Class to be extended by all the objects that can be used in tool executions as argument."""

    class Meta:
        """Model metadata."""

        abstract = True  # To be extended by models that can be used in tool executions as argument

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
        schema = "{protocol}://{host}/{endpoint}"
        if port:
            schema = "{protocol}://{host}:{port}/{endpoint}"  # Include port schema if port exists
        for protocol in protocols:  # For each protocol
            url_to_test = schema.format(
                protocol=protocol, host=host, port=port, endpoint=endpoint
            )
            try:
                # nosemgrep: python.requests.security.disabled-cert-validation.disabled-cert-validation
                requests.get(url_to_test, timeout=5, verify=False)
                return url_to_test
            except Exception:
                continue
        return None

    def _compare_filter(
        self, filter: Any, value: Any, negative: bool = False, contains: bool = False
    ) -> bool:
        comparison = lambda f, v: f == v if not contains else f in v
        return (
            comparison(filter, value) if not negative else not comparison(filter, value)
        )

    def filter(self, input: Any) -> bool:
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
                    ) or self._compare_filter(
                        filter.type(getattr(self, filter_value)),
                        field_value,
                        negative,
                        filter.contains,
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

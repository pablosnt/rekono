from typing import List

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import Field
from taggit.serializers import TagListSerializerField


@extend_schema_field({"type": "array", "items": {"type": "string"}})
class TagField(TagListSerializerField):
    """Internal serializer field for TagListSerializerField, including API documentation."""

    pass


@extend_schema_field(OpenApiTypes.STR)
class ProtectedSecretField(Field):
    """Serializer field to manage protected system values."""

    def __init__(
        self,
        validator: callable = None,
        read_only=False,
        write_only=False,
        required=None,
        source=None,
        label=None,
        help_text=None,
        style=None,
        error_messages=None,
        validators=None,
        allow_null=False,
    ):
        self.validator = validator
        super().__init__(
            read_only=read_only,
            write_only=write_only,
            required=required,
            source=source,
            label=label,
            help_text=help_text,
            style=style,
            error_messages=error_messages,
            validators=validators,
            allow_null=allow_null,
        )

    def to_representation(self, value: str) -> str:
        """Return text value to send to the client.

        Args:
            value (str): Internal text value

        Returns:
            str: Text value that contains multiple '*' characters
        """
        return "*" * len(value)

    def to_internal_value(self, value: str) -> str:
        """Return text value to be stored in database.

        Args:
            value (str): Text value provided by the client

        Returns:
            str: Text value to be stored. Save value than the provided one.
        """
        if self.validator:
            self.validator(value)
        return value


@extend_schema_field({"type": "array", "items": {"type": "string"}})
class StringAsListField(Field):
    def __init__(
        self,
        validator: callable = None,
        separator: str = ",",
        read_only=False,
        write_only=False,
        required=None,
        source=None,
        label=None,
        help_text=None,
        style=None,
        error_messages=None,
        validators=None,
        allow_null=False,
    ):
        self.validator = validator
        self.separator = separator
        super().__init__(
            read_only=read_only,
            write_only=write_only,
            required=required,
            source=source,
            label=label,
            help_text=help_text,
            style=style,
            error_messages=error_messages,
            validators=validators,
            allow_null=allow_null,
        )

    def to_representation(self, value: str) -> List[str]:
        return (value or "").split(self.separator)

    def to_internal_value(self, value: List[str]) -> str:
        if self.validator:
            for item in value:
                self.validator(item)
        return self.separator.join(value)
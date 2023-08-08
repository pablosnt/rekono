from django.forms import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import Field
from security.input_validation import validate_secret
from taggit.serializers import TagListSerializerField


@extend_schema_field({"type": "array", "items": {"type": "string"}})
class TagField(TagListSerializerField):
    """Internal serializer field for TagListSerializerField, including API documentation."""

    pass


@extend_schema_field(OpenApiTypes.STR)
class ProtectedSecretField(Field):
    """Serializer field to manage protected system values."""

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
        if validate_secret(value):
            return value
        raise ValidationError(["Value contains unallowed characters"])

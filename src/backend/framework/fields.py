"""Custom serializer fields for Django REST framework.

Provides specialized field types for tags, protected secrets, and
integer choices with enhanced security and API documentation features.
"""

from typing import Any, Callable

from django.core.exceptions import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import Field
from taggit.serializers import TagListSerializerField


@extend_schema_field({"type": "array", "items": {"type": "string"}})
class TagField(TagListSerializerField):
    """Serializer field for tag lists with proper OpenAPI documentation.

    Extends TagListSerializerField with enhanced OpenAPI schema definitions
    for automatic API documentation generation.

    Example:
        ```python
        class MySerializer(ModelSerializer):
            tags = TagField()
        ```
    """

    pass


@extend_schema_field(OpenApiTypes.STR)
class ProtectedSecretField(Field):
    """Serializer field for protected secret values.

    Provides secure handling of sensitive data by masking values in responses
    while allowing secure input validation and storage.

    Security Features:
        - Output values are masked with asterisks
        - Input validation through custom validator functions
        - No exposure of actual secret values in API responses

    Attributes:
        validator (Callable | None): Optional validation function for input values.

    Example:
        ```python
        class AuthSerializer(ModelSerializer):
            password = ProtectedSecretField(
                validator=lambda x: len(x) >= 8,
                write_only=True
            )
        ```
    """

    def __init__(
        self,
        validator: Callable | None = None,
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
        """Initialize the protected secret field.

        Args:
            validator (Callable | None): Optional validation function for input values.
            read_only (bool): Whether the field is read-only.
            write_only (bool): Whether the field is write-only.
            required (bool | None): Whether the field is required.
            source (str | None): Source attribute name.
            label (str | None): Human-readable label.
            help_text (str | None): Help text for documentation.
            style (dict | None): Styling information.
            error_messages (dict | None): Custom error messages.
            validators (list | None): Additional validators.
            allow_null (bool): Whether null values are allowed.
        """
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
        """Convert internal value to external representation.

        Masks the secret value with asterisks for security.

        Args:
            value (str): The internal secret value.

        Returns:
            str: Masked representation with asterisks.
        """
        return "*" * len(value)

    def to_internal_value(self, value: str) -> str:
        """Convert external representation to internal value.

        Validates the input value using the configured validator if present.

        Args:
            value (str): The input value to validate and store.

        Returns:
            str: The validated internal value.

        Raises:
            ValidationError: If validation fails.
        """
        if self.validator:
            self.validator(value)
        return value


@extend_schema_field(OpenApiTypes.STR)
class IntegerChoicesField(Field):
    """Serializer field for integer-based choice fields.

    Converts between integer values stored in the database and
    human-readable string representations for API responses.

    Attributes:
        model (Any): The choice model/enum class for value conversion.

    Example:
        ```python
        class StatusSerializer(ModelSerializer):
            status = IntegerChoicesField(model=StatusEnum)
        ```
    """

    def __init__(self, model: Any, **kwargs: Any):
        """Initialize the integer choices field.

        Args:
            model (Any): The choice model/enum class for conversions.
            **kwargs (Any): Additional field arguments.
        """
        self.model = model
        super().__init__(**kwargs)

    def to_representation(self, value: int) -> str:
        """Convert integer value to string representation.

        Args:
            value (int): The integer choice value.

        Returns:
            str: Capitalized string representation of the choice.
        """
        return self.model(value).name.capitalize()

    def to_internal_value(self, data: str) -> int:
        """Convert string representation to integer value.

        Args:
            data (str): The string choice representation.

        Returns:
            int: The corresponding integer value.

        Raises:
            ValidationError: If the string value is not valid.
        """
        try:
            return self.model[data.upper()].value
        except Exception:
            raise ValidationError("Invalid value", code=self.model.__class__.__name__)

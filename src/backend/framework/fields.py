from typing import Any, Callable

from django.core.exceptions import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import Field
from taggit.serializers import TagListSerializerField


@extend_schema_field({"type": "array", "items": {"type": "string"}})
class TagField(TagListSerializerField):
    """Custom tag field with OpenAPI schema extension.

    This field extends TagListSerializerField to provide proper OpenAPI
    documentation for tag arrays.
    """

    pass


@extend_schema_field(OpenApiTypes.STR)
class ProtectedSecretField(Field):
    """Field for handling sensitive data with protection.

    This field provides functionality for handling secret/sensitive data
    with automatic masking in serialization and optional validation.

    Attributes:
        validator (Callable): Optional validation function for the secret value.
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
            validator: Optional validation function for the secret value.
            read_only: Whether the field is read-only.
            write_only: Whether the field is write-only.
            required: Whether the field is required.
            source: The source attribute name.
            label: The field label.
            help_text: Help text for the field.
            style: The field style.
            error_messages: Custom error messages.
            validators: Additional validators.
            allow_null: Whether null values are allowed.
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
        """Convert the field value to its representation.

        Masks the secret value with asterisks for security.

        Args:
            value: The secret value to represent.

        Returns:
            Masked representation of the secret value.
        """
        return "*" * len(value)

    def to_internal_value(self, value: str) -> str:
        """Convert the input value to internal format.

        Validates the value if a validator is configured.

        Args:
            value: The input value to process.

        Returns:
            The validated secret value.

        Raises:
            ValidationError: If validation fails.
        """
        if self.validator:
            self.validator(value)
        return value


@extend_schema_field(OpenApiTypes.STR)
class IntegerChoicesField(Field):
    """Field for handling integer choice enums.

    This field provides serialization and deserialization for integer
    choice enums, converting between integer values and string names.

    Attributes:
        model: The choice enum class to use for conversion.
    """

    def __init__(self, model: Any, **kwargs: Any):
        """Initialize the integer choices field.

        Args:
            model: The choice enum class to use for conversion.
            **kwargs: Additional field configuration.
        """
        self.model = model
        super().__init__(**kwargs)

    def to_representation(self, value: int) -> str:
        """Convert integer value to string representation.

        Args:
            value: The integer value to convert.

        Returns:
            The capitalized name of the choice enum value.
        """
        return self.model(value).name.capitalize()

    def to_internal_value(self, data: str) -> int:
        """Convert string input to integer value.

        Args:
            data: The string input to convert.

        Returns:
            The integer value of the choice enum.

        Raises:
            ValidationError: If the input is not a valid choice.
        """
        try:
            return self.model[data.upper()].value
        except Exception:
            raise ValidationError("Invalid value", code=self.model.__class__.__name__)

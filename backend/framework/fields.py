"""Custom serializer fields shared by the Rekono API.

Cover the cases where the value exposed by the API doesn't match the one stored in
the database: tags, encrypted secrets, and integer choices exposed by name.
"""

from typing import Any

from django.core.exceptions import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import Field
from taggit.serializers import TagListSerializerField


@extend_schema_field({"type": "array", "items": {"type": "string"}})
class TagField(TagListSerializerField):
    """List of tags, documented as an array of strings in the OpenAPI schema."""

    pass


@extend_schema_field(OpenApiTypes.STR)
class ProtectedSecretField(Field):
    """Secret value that is never returned to the API clients.

    Expects to be declared on a ModelSerializer whose Meta.model is a BaseEncrypted
    subclass, since both the validation and the storage are delegated to that
    model's encrypted field.
    """

    def to_representation(self, value: str) -> str:
        """Mask the secret with one asterisk per character.

        Args:
            value: Decrypted secret read from the model.

        Returns:
            A masked value that keeps the length of the secret, so the clients can
            tell whether a secret is configured without ever receiving it.
        """
        return "*" * len(value)

    def to_internal_value(self, value: str) -> str:
        """Validate the secret against the encrypted field that will store it.

        Looks up the encrypted field declared on the parent serializer's
        Meta.model (via its _encrypted_field attribute) and enforces that
        field's max_length and validators against the incoming value.

        Args:
            value: Plain secret sent by the client, before it is encrypted.

        Returns:
            The value unchanged, since the encryption happens when the model is
            saved and not in this field.

        Raises:
            ValidationError: If the value exceeds the encrypted field's max_length
              or fails its validators.
        """
        model = self.parent.Meta.model
        field = model._meta.get_field(model._encrypted_field)
        if hasattr(field, "max_length") and field.max_length and len(value) > field.max_length:
            # Strip the leading underscore from the private field name (e.g. "_api_token")
            # so the error code matches the public field name exposed by the serializer
            raise ValidationError("Value exceeds the maximum allowed length", code=model._encrypted_field[1:])
        field.run_validators(value)
        return value


@extend_schema_field(OpenApiTypes.STR)
class IntegerChoicesField(Field):
    """Choice stored as an integer and exposed by its name in the API.

    Attributes:
        model: Enumeration that maps the names exposed by the API to the integer
          values stored in the database.
    """

    def __init__(self, model: Any, **kwargs: Any):
        """Prepare the field with the enumeration used to convert the values.

        Args:
            model: Enumeration that provides the names and values of the choices.
            **kwargs: Standard serializer field arguments.
        """
        self.model = model
        super().__init__(**kwargs)

    def to_representation(self, value: int) -> str:
        """Get the capitalized name of the choice with the given value.

        Args:
            value: Integer stored in the database.

        Returns:
            The name of the matching choice, capitalized for the API clients.
        """
        return self.model(value).name.capitalize()

    def to_internal_value(self, data: str) -> int:
        """Get the value of the choice with the given name, ignoring the case.

        Args:
            data: Name of the choice sent by the client, in any case.

        Returns:
            The integer value to store in the database.

        Raises:
            ValidationError: If there is no choice with that name.
        """
        try:
            return self.model[data.upper()].value
        except Exception:
            raise ValidationError("Invalid value", code=self.model.__class__.__name__)

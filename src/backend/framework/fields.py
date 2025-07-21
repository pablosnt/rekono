from typing import Any, Callable

from django.core.exceptions import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import Field
from taggit.serializers import TagListSerializerField


@extend_schema_field({"type": "array", "items": {"type": "string"}})
class TagField(TagListSerializerField):
    pass


@extend_schema_field(OpenApiTypes.STR)
class ProtectedSecretField(Field):
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
        return "*" * len(value)

    def to_internal_value(self, value: str) -> str:
        if self.validator:
            self.validator(value)
        return value


@extend_schema_field(OpenApiTypes.STR)
class IntegerChoicesField(Field):
    def __init__(self, model: Any, **kwargs: Any):
        self.model = model
        super().__init__(**kwargs)

    def to_representation(self, value: int) -> str:
        return self.model(value).name.capitalize()

    def to_internal_value(self, data: str) -> int:
        try:
            return self.model[data.upper()].value
        except Exception:
            raise ValidationError("Invalid value", code=self.model.__class__.__name__)

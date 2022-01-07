from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


@extend_schema_field(OpenApiTypes.STR)
class IntegerChoicesField(serializers.Field):

    def to_representation(self, value: int) -> str:
        return self.model(value).name.capitalize()

    def to_internal_value(self, data: str) -> int:
        return self.model[data.upper()].value

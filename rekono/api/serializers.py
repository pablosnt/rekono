from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from taggit.serializers import TagListSerializerField


@extend_schema_field(OpenApiTypes.STR)
class IntegerChoicesField(serializers.Field):
    '''Serializer field to manage IntegerChoices values.'''

    def to_representation(self, value: int) -> str:
        '''Return text value to send to the client.

        Args:
            value (int): Integer value of the IntegerChoices field

        Returns:
            str: String value associated to the integer
        '''
        return self.model(value).name.capitalize()

    def to_internal_value(self, data: str) -> int:
        '''Return integer value to be stored in database.

        Args:
            data (str): String value of the IntegerChoices field

        Returns:
            int: Integer value associated to the string
        '''
        return self.model[data.upper()].value


@extend_schema_field({'type': 'array', 'items': {'type': 'string'}})
class RekonoTagSerializerField(TagListSerializerField):
    '''Internal serializer field for TagListSerializerField, including API documentation.'''

    pass

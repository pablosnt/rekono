from rest_framework import serializers


class IntegerChoicesField(serializers.Field):

    def to_representation(self, value: int) -> str:
        return self.model(value).name.capitalize()

    def to_internal_value(self, data: str) -> int:
        return self.model[data.upper()].value

from rest_framework import serializers


class IntegerChoicesField(serializers.Field):

    def to_representation(self, value):
        return self.model(value).name.capitalize()

    def to_internal_value(self, data):
        return self.model[data.upper()].value

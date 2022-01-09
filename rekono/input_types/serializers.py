from input_types.models import InputType
from rest_framework import serializers


class InputTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = InputType
        fields = ('name', 'callback_target')
        ordering = ['-id']

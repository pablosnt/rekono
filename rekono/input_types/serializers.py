from rest_framework import serializers

from input_types.models import InputType


class InputTypeSerializer(serializers.ModelSerializer):
    '''Serializer to get the input type data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = InputType
        fields = ('name', 'model', 'callback_model')                            # Input type fields exposed via API

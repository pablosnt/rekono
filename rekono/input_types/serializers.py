from input_types.models import InputType
from rest_framework import serializers


class InputTypeSerializer(serializers.ModelSerializer):
    '''Serializer to get the input type data via API.'''

    class Meta:
        '''Serializer metadata.'''

        model = InputType
        fields = ('name', 'callback_target')                                    # Input type fields exposed via API

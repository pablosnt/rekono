from typing import Any, Dict

from api.serializers import ProtectedStringValueField
from django.forms import ValidationError
from rest_framework import serializers
from security.input_validation import validate_credential

from authentication.models import Authentication


class AuthenticationSerializer(serializers.ModelSerializer):
    '''Serializer to manage authentications via API.'''

    credential = ProtectedStringValueField(required=True, allow_null=False)

    class Meta:

        model = Authentication
        fields = ('id', 'target_port', 'name', 'credential', 'type')

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        '''Validate the provided data before use it.

        Args:
            attrs (Dict[str, Any]): Provided data

        Raises:
            ValidationError: Raised if provided data is invalid

        Returns:
            Dict[str, Any]: Data after validation process
        '''
        attrs = super().validate(attrs)
        validate_credential(attrs['credential'])
        if Authentication.objects.get(target_port=attrs['target_port']).exists():
            raise ValidationError({
                'name': 'This name already exists in this target port',
                'credential': 'This credential already exists for this technology in this target port',
                'type': 'This credential type already exists for this technology in this target port'
            })
        return attrs

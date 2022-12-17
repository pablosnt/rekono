from typing import Any, Dict

from api.fields import ProtectedStringValueField
from rest_framework import serializers
from security.input_validation import validate_credential

from authentications.models import Authentication


class AuthenticationSerializer(serializers.ModelSerializer):
    '''Serializer to manage authentications via API.'''

    credential = ProtectedStringValueField(required=True, allow_null=False)     # Credential value in a protected way

    class Meta:
        '''Serializer metadata.'''

        model = Authentication
        fields = ('id', 'target_port', 'name', 'credential', 'type')            # Authentication fields exposed via API

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
        return attrs

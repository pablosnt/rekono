from typing import Any, Dict, Optional

from api.fields import ProtectedStringValueField
from defectdojo.api import DefectDojo
from rest_framework import serializers
from security.input_validation import (validate_defect_dojo_api_key,
                                       validate_telegram_token)
from telegram_bot.bot import get_telegram_bot_name

from system.models import System


class SystemSerializer(serializers.ModelSerializer):
    '''Serializer to manage system settings via API.'''

    # Telegram bot name obtained automatically using the Telegram token
    telegram_bot_name = serializers.SerializerMethodField(method_name='get_telegram_bot_name', read_only=True)
    # Telegram token in a protected way
    telegram_bot_token = ProtectedStringValueField(required=False, allow_null=True)
    # Defect-Dojo APi key in a protected way
    defect_dojo_api_key = ProtectedStringValueField(required=False, allow_null=True)
    # Indicate if Defect-Dojo integration is available using the URL and the API key
    defect_dojo_enabled = serializers.SerializerMethodField(method_name='is_defect_dojo_enabled', read_only=True)

    class Meta:
        '''Serializer metadata.'''

        model = System
        fields = (                                                              # System fields exposed via API
            'id', 'upload_files_max_mb', 'telegram_bot_name', 'telegram_bot_token',
            'defect_dojo_url', 'defect_dojo_api_key', 'defect_dojo_verify_tls',
            'defect_dojo_tag', 'defect_dojo_product_type', 'defect_dojo_test_type',
            'defect_dojo_test', 'defect_dojo_enabled'
        )

    def is_defect_dojo_enabled(self, instance: System) -> bool:
        '''Indicate if Defect-Dojo integration is available using the URL and the API key.

        Args:
            instance (System): System instance. Not used.

        Returns:
            bool: Indicate if Defect-Dojo integration is available
        '''
        dd_client = DefectDojo()
        return dd_client.is_available()

    def get_telegram_bot_name(self, instance: System) -> Optional[str]:
        '''Get Telegram bot name using the Telegram bot.

        Args:
            instance (System): System instance. Not used

        Returns:
            Optional[str]: Telegram bot name
        '''
        return get_telegram_bot_name()

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
        if 'telegram_bot_token' in attrs:
            validate_telegram_token(attrs.get('telegram_bot_token', ''))
        if 'defect_dojo_api_key' in attrs:
            validate_defect_dojo_api_key(attrs.get('defect_dojo_api_key', ''))
        return attrs

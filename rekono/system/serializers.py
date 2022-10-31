from typing import Optional

from defectdojo.api import DefectDojo
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from telegram_bot.bot import get_telegram_bot_name

from system.models import System


@extend_schema_field(OpenApiTypes.STR)
class ProtectedValueField(serializers.Field):
    '''Serializer field to manage protected system values.'''

    def to_representation(self, value: str) -> str:
        '''Return text value to send to the client.

        Args:
            value (str): Internal text value

        Returns:
            str: Text value that contains multiple '*' characters
        '''
        return '*' * len(value)

    def to_internal_value(self, value: str) -> str:
        '''Return text value to be stored in database.

        Args:
            value (str): Text value provided by the client

        Returns:
            str: Text value to be stored. Save value than the provided one.
        '''
        return value


class SystemSerializer(serializers.ModelSerializer):
    '''Serializer to manage system settings via API.'''

    # Telegram bot name obtained automatically using the Telegram token
    telegram_bot_name = serializers.SerializerMethodField(method_name='get_telegram_bot_name', read_only=True)
    # Telegram token in a protected way
    telegram_bot_token = ProtectedValueField(required=False, allow_null=True)
    # Defect-Dojo APi key in a protected way
    defect_dojo_api_key = ProtectedValueField(required=False, allow_null=True)
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

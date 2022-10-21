from defectdojo.api import DefectDojo
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from telegram_bot.utils import get_telegram_bot_name

from settings.models import Setting


@extend_schema_field(OpenApiTypes.STR)
class ProtectedValueField(serializers.Field):

    def to_representation(self, value: str) -> str:
        return '*' * len(value)

    def to_internal_value(self, value: str) -> str:
        return value


class SettingSerializer(serializers.ModelSerializer):

    telegram_bot_name = serializers.SerializerMethodField(method_name='get_telegram_bot_name', read_only=True)
    telegram_bot_token = ProtectedValueField(source='telegram_bot_token')
    defect_dojo_api_key = ProtectedValueField(source='defect_dojo_api_key')
    defect_dojo_enabled = serializers.SerializerMethodField(method_name='is_defect_dojo_enabled', read_only=True)

    class Meta:
        model = Setting
        fields = (
            'id', 'upload_files_max_mb', 'telegram_bot_token', 'defect_dojo_url',
            'defect_dojo_api_key', 'defect_dojo_verify_tls', 'defect_dojo_tag',
            'defect_dojo_product_type', 'defect_dojo_test_type', 'defect_dojo_test'
        )
    
    def is_defect_dojo_enabled(self) -> bool:
        dd_client = DefectDojo()
        return dd_client.is_available()

    def get_telegram_bot_name(self) -> str:
        return get_telegram_bot_name()

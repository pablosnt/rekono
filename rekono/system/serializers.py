from typing import Optional

from defectdojo.api import DefectDojo
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from telegram_bot.utils import get_telegram_bot_name

from system.models import System


@extend_schema_field(OpenApiTypes.STR)
class ProtectedValueField(serializers.Field):

    def to_representation(self, value: str) -> str:
        return '*' * len(value)

    def to_internal_value(self, value: str) -> str:
        return value


class SystemSerializer(serializers.ModelSerializer):

    telegram_bot_name = serializers.SerializerMethodField(method_name='get_telegram_bot_name', read_only=True)
    telegram_bot_token = ProtectedValueField(required=False, allow_null=True)
    defect_dojo_api_key = ProtectedValueField(required=False, allow_null=True)
    defect_dojo_enabled = serializers.SerializerMethodField(method_name='is_defect_dojo_enabled', read_only=True)

    class Meta:
        model = System
        fields = (
            'id', 'upload_files_max_mb', 'telegram_bot_name', 'telegram_bot_token',
            'defect_dojo_url', 'defect_dojo_api_key', 'defect_dojo_verify_tls',
            'defect_dojo_tag', 'defect_dojo_product_type', 'defect_dojo_test_type',
            'defect_dojo_test', 'defect_dojo_enabled'
        )

    def is_defect_dojo_enabled(self, instance: System) -> bool:
        dd_client = DefectDojo()
        return dd_client.is_available()

    def get_telegram_bot_name(self, instance: System) -> Optional[str]:
        return get_telegram_bot_name()

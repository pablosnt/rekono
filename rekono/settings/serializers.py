from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from security.input_validation import (DD_KEY_REGEX, TELEGRAM_TOKEN_REGEX,
                                       validate_boolean_value, validate_name,
                                       validate_number_value,
                                       validate_text_value, validate_url)

from settings.models import Setting


@extend_schema_field(OpenApiTypes.STR)
class SettingValueField(serializers.Field):

    def get_attribute(self, instance):
        return instance

    def to_representation(self, instance: Setting) -> str:
        if instance.private and instance.value:
            return '*' * len(instance.value)
        return instance.value

    def to_internal_value(self, value: str) -> str:
        return value


class SettingSerializer(serializers.ModelSerializer):

    value = SettingValueField()

    class Meta:
        model = Setting
        fields = ('id', 'field', 'value', 'private', 'last_modified')
        read_only_fields = ('field', 'private', 'last_modified')

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)
        validators = {
            'otp_expiration_hours': (int, validate_number_value, [1, 72]),
            'upload_files_max_mb': (int, validate_number_value, [100, 1000]),
            'telegram_bot_token': (str, validate_text_value, [TELEGRAM_TOKEN_REGEX]),
            'defect_dojo_url': (str, validate_url, []),
            'defect_dojo_api_key': (str, validate_text_value, [DD_KEY_REGEX]),
            'defect_dojo_verify_tls': (None, validate_boolean_value, []),
            'defect_dojo_tag': (str, validate_name, []),
            'defect_dojo_product_type': (str, validate_name, []),
            'defect_dojo_test_type': (str, validate_name, []),
            'defect_dojo_test': (str, validate_name, []),
        }
        value_type, validator, args = validators[self.instance.field]
        value = self.value if not value_type else value_type(attrs.get('value'))
        args.insert(0, value)
        validator(*args)
        return validated_attrs

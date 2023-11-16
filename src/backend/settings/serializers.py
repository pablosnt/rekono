from framework.fields import StringAsListField
from rest_framework.serializers import ModelSerializer
from security.input_validator import Regex, Validator
from settings.models import Settings


class SettingsSerializer(ModelSerializer):
    """Serializer to manage system settings via API."""

    # # Telegram bot name obtained automatically using the Telegram token
    # telegram_bot_name = serializers.SerializerMethodField(method_name='get_telegram_bot_name', read_only=True)
    # # Telegram token in a protected way
    # telegram_bot_token = ProtectedStringValueField(required=False, allow_null=True)
    target_blacklist = StringAsListField(
        Validator(Regex.TARGET_REGEX.value, code="target_blacklist").__call__,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Settings
        fields = (
            "id",
            "max_uploaded_file_mb",
            "target_blacklist",
        )

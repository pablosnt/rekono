from framework.fields import ProtectedSecretField
from platforms.mail.models import SMTPSettings
from platforms.mail.notifications import SMTP
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from security.validators.input_validator import Regex, Validator


class SMTPSettingsSerializer(ModelSerializer):
    password = ProtectedSecretField(
        Validator(Regex.SECRET.value, code="password").__call__,
        required=False,
        allow_null=True,
        source="secret",
    )
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        model = SMTPSettings
        fields = ("id", "host", "port", "username", "password", "tls", "is_available")

    def get_is_available(self, instance: SMTPSettings) -> bool:
        return SMTP().is_available()

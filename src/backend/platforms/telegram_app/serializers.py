import logging
from typing import Any, Dict

from django.utils import timezone
from framework.fields import ProtectedSecretField
from platforms.mail.notifications import SMTP
from platforms.telegram_app.models import TelegramChat, TelegramSettings
from platforms.telegram_app.notifications.notifications import Telegram
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from security.input_validator import Regex, Validator

logger = logging.getLogger()


class TelegramSettingsSerializer(ModelSerializer):
    token = ProtectedSecretField(
        Validator(Regex.SECRET.value, code="password").__call__,
        write_only=True,
        required=True,
        source="secret",
    )
    bot = SerializerMethodField(method_name="get_bot_name", read_only=True)
    is_available = SerializerMethodField(method_name="is_available", read_only=True)

    class Meta:
        model = TelegramSettings
        fields = ("id", "bot", "token")

    def get_bot_name(self, instance: TelegramSettings) -> str:
        telegram = Telegram()
        telegram.initialize()
        return telegram.get_bot_name()

    def is_available(self, instance: TelegramSettings) -> bool:
        return Telegram().is_available()


class TelegramChatSerializer(ModelSerializer):
    class Meta:
        model = TelegramChat
        fields = (
            "id",
            "otp",
            "user",
        )
        read_only_fields = ("user",)
        extra_kwargs = {"otp": {"write_only": True}}

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        try:
            attrs["telegram_chat"] = TelegramChat.objects.get(
                otp=attrs.get("otp"),
                otp_expiration__gt=timezone.now(),
                user=None,
            )
        except TelegramChat.DoesNotExist:
            raise AuthenticationFailed(
                "Invalid Telegram OTP", code=status.HTTP_401_UNAUTHORIZED
            )
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> TelegramChat:
        validated_data["telegram_chat"].otp = None
        validated_data["telegram_chat"].otp_expiration = None
        validated_data["telegram_chat"].user = validated_data["user"]
        validated_data["telegram_chat"].save(
            update_fields=["otp", "otp_expiration", "user"]
        )
        SMTP().telegram_linked_notification(validated_data["user"])
        Telegram().welcome_message(validated_data["telegram_chat"])
        logger.info(
            f"[Security] User {validated_data['user'].id} has logged in the Telegram bot",
            extra={"user": validated_data["user"].id},
        )
        return validated_data["telegram_chat"]

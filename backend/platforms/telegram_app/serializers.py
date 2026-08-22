"""Serializers of the Telegram endpoints."""

from typing import Any

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from framework.logging import LoggingEntity
from platforms.email.notifications import SMTP
from platforms.telegram_app.models import TelegramChat, TelegramSettings
from platforms.telegram_app.notifications import Telegram
from security.cryptography import Crypto


class TelegramSettingsSerializer(ModelSerializer):
    """Serializer of the Telegram configuration.

    Attributes:
        token: Bot token, which is masked when the settings are read.
        bot: Name of the bot that the configured token belongs to.
        is_available: Whether Telegram accepts the configured token.
    """

    token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    bot = SerializerMethodField(read_only=True)
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        """Serializer configuration for the Telegram settings."""

        model = TelegramSettings
        fields = ("id", "token", "bot", "is_available")

    @property
    def client(self) -> Telegram:
        """A bot client prepared with the configuration that is stored now."""
        client = Telegram()
        client.initialize()
        client.settings = TelegramSettings.objects.first()
        return client

    def get_bot(self, instance: TelegramSettings) -> str | None:
        """Get the name of the bot that the configured token belongs to.

        Args:
            instance: Settings being serialized, not read because the name comes
              from Telegram itself.

        Returns:
            The name of the bot, or None if Telegram rejects the configured token.
        """
        return self.client.bot_name

    def get_is_available(self, instance: TelegramSettings) -> bool:
        """Check if Telegram accepts the configured token.

        Args:
            instance: Settings being serialized, not read because the check is
              performed against the live platform.

        Returns:
            Whether the platform answers with the configured settings.
        """
        return self.client.is_available()


class TelegramChatSerializer(ModelSerializer, LoggingEntity):
    """Serializer of the link between a Telegram chat and a Rekono account."""

    class Meta:
        """Serializer configuration for the Telegram chats."""

        model = TelegramChat
        fields = ("id", "otp", "user")
        read_only_fields = ("user",)
        extra_kwargs = {"otp": {"write_only": True}}

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the code that the bot gave and find the chat that it belongs to.

        Args:
            attrs: Validated data including the one-time password that the bot
              showed in the Telegram conversation.

        Returns:
            The validated data, with the chat that will be linked.

        Raises:
            ValidationError: If the user already has a linked chat.
            AuthenticationFailed: If the code is wrong, if it expired, or if the
                chat was linked by somebody else in the meantime.
        """
        attrs = super().validate(attrs)
        request = self.context.get("request")
        # A user can only link one chat
        if request and hasattr(request.user, "telegram_chat"):
            raise ValidationError("This account is already linked to a Telegram chat")
        try:
            attrs["telegram_chat"] = TelegramChat.objects.get(
                otp=Crypto.hash(attrs.get("otp")), otp_expiration__gt=timezone.now(), user=None
            )
        except TelegramChat.DoesNotExist:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs

    def create(self, validated_data: dict[str, Any]) -> TelegramChat:
        """Link the chat to the account and tell the user about it.

        Args:
            validated_data: The user, and the telegram_chat that the validate
                method resolves from the code that was sent, since the chat itself
                is never part of the request.

        Returns:
            The linked chat, whose code is removed so it can't be used again.
        """
        validated_data["telegram_chat"].otp = None
        validated_data["telegram_chat"].otp_expiration = None
        validated_data["telegram_chat"].user = validated_data["user"]
        validated_data["telegram_chat"].save(update_fields=["otp", "otp_expiration", "user"])
        SMTP().telegram_linked_notification(validated_data["user"])
        Telegram().welcome_message(validated_data["user"])
        self.logger.info(
            f"[Security] User {validated_data['user'].id} has logged in the Telegram bot",
            extra={"user": validated_data["user"].id},
        )
        return validated_data["telegram_chat"]

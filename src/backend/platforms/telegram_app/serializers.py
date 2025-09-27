"""Serializers for Telegram Bot models with secure OTP validation and linking.

Provides serialization for Telegram settings and chat management including
secure One-Time Password validation and user account linking workflows.
"""

from typing import Any

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from framework.logging import LoggingEntity
from platforms.mail.notifications import SMTP
from platforms.telegram_app.models import TelegramChat, TelegramSettings
from platforms.telegram_app.notifications import Telegram
from security.cryptography import Crypto


class TelegramSettingsSerializer(ModelSerializer, LoggingEntity):
    """Serializer for Telegram Bot settings with encrypted token handling.

    Handles serialization and validation of Telegram Bot configuration including
    encrypted token management and bot availability status checks.

    Attributes:
        token (ProtectedSecretField): Encrypted Bot API token field with validation
        bot (SerializerMethodField): Read-only bot name information
        is_available (SerializerMethodField): Bot availability status check
        client (Telegram): Telegram client instance for status checks
    """

    token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    bot = SerializerMethodField(read_only=True)
    is_available = SerializerMethodField(read_only=True)

    client = Telegram()

    class Meta:
        """Meta configuration for TelegramSettingsSerializer.

        Attributes:
            model (Model): The TelegramSettings model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = TelegramSettings
        fields = ("id", "token", "bot", "is_available")

    def get_bot(self, instance: TelegramSettings) -> str | None:
        """Get the Telegram Bot name from the client.

        Args:
            instance (TelegramSettings): The settings instance being serialized.

        Returns:
            str | None: The Bot name if available, None otherwise.
        """
        return self.client.bot_name

    def get_is_available(self, instance: TelegramSettings) -> bool:
        """Check if the Telegram Bot is available and configured.

        Args:
            instance (TelegramSettings): The settings instance being serialized.

        Returns:
            bool: True if the Bot is configured and available.
        """
        return self.client.is_available()


class TelegramChatSerializer(ModelSerializer, LoggingEntity):
    """Serializer for Telegram chat account linking with OTP validation.

    Handles the secure account linking process using One-Time Passwords (OTP)
    including validation, expiration checking, and notification delivery.
    """

    class Meta:
        """Meta configuration for TelegramChatSerializer.

        Attributes:
            model (Model): The TelegramChat model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that are read-only in API operations
            extra_kwargs (dict): Additional field configuration options
        """

        model = TelegramChat
        fields = ("id", "otp", "user")
        read_only_fields = ("user",)
        extra_kwargs = {"otp": {"write_only": True}}

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate OTP and retrieve the corresponding Telegram chat.

        Validates the provided OTP against existing chats with unexpired OTPs
        and no linked user account.

        Args:
            attrs (dict[str, Any]): Serializer attributes to validate.

        Returns:
            dict[str, Any]: Validated attributes with matched Telegram chat.

        Raises:
            AuthenticationFailed: If OTP is invalid or expired.
        """
        attrs = super().validate(attrs)
        try:
            attrs["telegram_chat"] = TelegramChat.objects.get(
                otp=Crypto.hash(attrs.get("otp")), otp_expiration__gt=timezone.now(), user=None
            )
        except TelegramChat.DoesNotExist:
            raise AuthenticationFailed(code=status.HTTP_401_UNAUTHORIZED)
        return attrs

    def create(self, validated_data: dict[str, Any]) -> TelegramChat:
        """Create user-chat link and send notifications.

        Links the Telegram chat to the user account, clears OTP data, and sends
        confirmation notifications via email and Telegram.

        Args:
            validated_data (dict[str, Any]): Validated serializer data.

        Returns:
            TelegramChat: The linked Telegram chat instance.
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

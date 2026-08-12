"""Viewsets of the Telegram endpoints."""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.telegram_app.models import TelegramChat, TelegramSettings
from platforms.telegram_app.serializers import (
    TelegramChatSerializer,
    TelegramSettingsSerializer,
)
from security.authorization.permissions import OwnerPermission, RekonoModelPermission


class TelegramSettingsViewSet(BaseViewSet):
    """Read and update the Telegram configuration.

    Attributes:
        queryset: The only settings instance, created by the migrations.
        serializer_class: Serializer of the Telegram settings.
        permission_classes: Only the users that can change the settings model.
        http_method_names: GET and PUT only, since the settings are never created
          or removed through the API.
    """

    queryset = TelegramSettings.objects.all()
    serializer_class = TelegramSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]


class TelegramChatViewSet(BaseViewSet):
    """Link a Telegram chat to the account of a user, or unlink it.

    Attributes:
        queryset: All the chats, filtered later by their owner.
        serializer_class: Serializer of the Telegram chats.
        permission_classes: Role permissions plus the ownership of the chat, so
          nobody can unlink the chat of another user.
        http_method_names: POST to link a chat and DELETE to unlink it.
        owner_field: Field with the user that the chat belongs to.
    """

    queryset = TelegramChat.objects.all()
    serializer_class = TelegramChatSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    http_method_names = ["post", "delete"]
    owner_field = "user"

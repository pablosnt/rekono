"""Django REST framework views for Telegram Bot configuration.

Provides REST API endpoints for managing Telegram Bot settings and chat
relationships with proper authentication and authorization controls.
"""

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from platforms.telegram_app.models import TelegramChat, TelegramSettings
from platforms.telegram_app.serializers import (
    TelegramChatSerializer,
    TelegramSettingsSerializer,
)
from security.authorization.permissions import OwnerPermission, RekonoModelPermission


class TelegramSettingsViewSet(BaseViewSet):
    """ViewSet for managing Telegram Bot configuration settings.

    Provides GET and PUT operations for Telegram Bot settings including
    encrypted token management with proper authentication controls.

    Attributes:
        queryset (QuerySet): TelegramSettings model instances
        serializer_class (Serializer): Serializer for TelegramSettings model
        permission_classes (list): Required permissions for access control
        http_method_names (list): Allowed HTTP methods (GET, PUT only)
    """

    queryset = TelegramSettings.objects.all()
    serializer_class = TelegramSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]


class TelegramChatViewSet(BaseViewSet):
    """ViewSet for managing Telegram chat account linking.

    Provides POST and DELETE operations for Telegram chat relationships
    with user-scoped access control and ownership permissions.

    Attributes:
        queryset (QuerySet): TelegramChat model instances
        serializer_class (Serializer): Serializer for TelegramChat model
        permission_classes (list): Required permissions for access control
        http_method_names (list): Allowed HTTP methods (POST, DELETE only)
        owner_field (str): Field name for ownership-based access control
    """

    queryset = TelegramChat.objects.all()
    serializer_class = TelegramChatSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    http_method_names = ["post", "delete"]
    owner_field = "user"

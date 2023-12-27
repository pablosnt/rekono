from framework.views import BaseViewSet
from platforms.telegram_app.models import TelegramChat, TelegramSettings
from platforms.telegram_app.serializers import (
    TelegramChatSerializer,
    TelegramSettingsSerializer,
)
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import OwnerPermission, RekonoModelPermission

# Create your views here.


class TelegramSettingsViewSet(BaseViewSet):
    queryset = TelegramSettings.objects.all()
    serializer_class = TelegramSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = [
        "get",
        "put",
    ]


class TelegramChatViewSet(BaseViewSet):
    queryset = TelegramChat.objects.all()
    serializer_class = TelegramChatSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission, OwnerPermission]
    http_method_names = ["post", "delete"]
    owner_field = "user"

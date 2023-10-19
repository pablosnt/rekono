from framework.views import BaseViewSet
from platforms.telegram_app.models import TelegramChat, TelegramSettings
from platforms.telegram_app.serializers import (
    TelegramChatSerializer,
    TelegramSettingsSerializer,
)

# Create your views here.


class TelegramSettingsViewSet(BaseViewSet):
    queryset = TelegramSettings.objects.all()
    serializer_class = TelegramSettingsSerializer
    http_method_names = [
        "get",
        "put",
    ]


class TelegramChatViewSet(BaseViewSet):
    queryset = TelegramChat.objects.all()
    serializer_class = TelegramChatSerializer
    http_method_names = ["post", "delete"]
    owner_field = "user"

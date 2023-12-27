from platforms.telegram_app.views import TelegramChatViewSet, TelegramSettingsViewSet
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register("telegram/settings", TelegramSettingsViewSet)
router.register("telegram/link", TelegramChatViewSet)

urlpatterns = router.urls

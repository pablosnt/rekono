"""URLs of the Telegram endpoints."""

from rest_framework.routers import SimpleRouter

from platforms.telegram_app.views import TelegramChatViewSet, TelegramSettingsViewSet

router = SimpleRouter()
router.register("telegram/settings", TelegramSettingsViewSet)
router.register("telegram/link", TelegramChatViewSet)

urlpatterns = router.urls

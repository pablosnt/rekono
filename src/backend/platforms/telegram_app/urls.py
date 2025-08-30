"""URL configuration for Telegram Bot REST API endpoints.

Defines URL routes for Telegram Bot settings management and chat linking
operations through Django REST framework ViewSets.
"""

from rest_framework.routers import SimpleRouter

from platforms.telegram_app.views import TelegramChatViewSet, TelegramSettingsViewSet

router = SimpleRouter()
router.register("telegram/settings", TelegramSettingsViewSet)
router.register("telegram/link", TelegramChatViewSet)

urlpatterns = router.urls

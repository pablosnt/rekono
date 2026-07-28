"""URL configuration for the settings module.

Defines URL patterns for the settings REST API endpoint, exposing global
platform configuration for viewing and updating.
"""

from rest_framework.routers import SimpleRouter

from settings.views import SettingsViewSet

router = SimpleRouter()
router.register("settings", SettingsViewSet)

urlpatterns = router.urls

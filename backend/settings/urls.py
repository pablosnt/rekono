"""Settings URL configuration for Rekono API.

This module defines URL routing for Settings API endpoints using Django REST
framework router configuration. Provides secure routing for administrative
access to global platform configuration management.
"""

from rest_framework.routers import SimpleRouter

from settings.views import SettingsViewSet

router = SimpleRouter()
router.register("settings", SettingsViewSet)

urlpatterns = router.urls

"""URL configuration for alerts module.

This module defines the URL patterns for the alerts REST API endpoints,
including alert management and monitoring settings.
"""

from rest_framework.routers import SimpleRouter

from alerts.views import AlertViewSet, MonitorSettingsViewSet

router = SimpleRouter()
router.register("alerts", AlertViewSet)
router.register("monitor", MonitorSettingsViewSet)

urlpatterns = router.urls

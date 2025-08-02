"""URL configuration for alerts module.

Defines URL patterns for the alerts REST API endpoints, including
alert management and monitoring settings routes.
"""

from rest_framework.routers import SimpleRouter

from alerts.views import AlertViewSet, MonitorSettingsViewSet

router = SimpleRouter()
router.register("alerts", AlertViewSet)
router.register("monitor", MonitorSettingsViewSet)

urlpatterns = router.urls

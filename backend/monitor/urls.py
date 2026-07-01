"""URL configuration for monitor module.

Defines URL patterns for the monitor REST API endpoint, exposing the
monitoring settings resource for viewing and updating.
"""

from rest_framework.routers import SimpleRouter

from monitor.views import MonitorSettingsViewSet

router = SimpleRouter()
router.register("monitor", MonitorSettingsViewSet)

urlpatterns = router.urls

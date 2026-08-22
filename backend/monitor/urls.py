"""URLs of the monitor endpoints."""

from rest_framework.routers import SimpleRouter

from monitor.views import MonitorSettingsViewSet

router = SimpleRouter()
router.register("monitor", MonitorSettingsViewSet)

urlpatterns = router.urls

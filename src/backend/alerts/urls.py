from rest_framework.routers import SimpleRouter

from alerts.views import AlertViewSet, MonitorSettingsViewSet

router = SimpleRouter()
router.register("alerts", AlertViewSet)
router.register("monitor", MonitorSettingsViewSet)

urlpatterns = router.urls

from alerts.views import AlertViewSet, MonitorSettingsViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("alerts", AlertViewSet)
router.register("monitor", MonitorSettingsViewSet)

urlpatterns = router.urls

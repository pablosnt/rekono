"""URLs of the DefectDojo endpoints."""

from rest_framework.routers import SimpleRouter

from platforms.defectdojo.views import DefectDojoSettingsViewSet, DefectDojoSyncViewSet

router = SimpleRouter()
router.register("defectdojo/settings", DefectDojoSettingsViewSet)
router.register("defectdojo/sync", DefectDojoSyncViewSet)

urlpatterns = router.urls

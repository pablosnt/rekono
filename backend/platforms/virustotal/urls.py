"""URLs of the VirusTotal endpoints."""

from rest_framework.routers import SimpleRouter

from platforms.virustotal.views import VirusTotalSettingsViewSet

router = SimpleRouter()
router.register("virustotal", VirusTotalSettingsViewSet)

urlpatterns = router.urls

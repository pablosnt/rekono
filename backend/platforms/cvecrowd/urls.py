"""URLs of the CVE Crowd endpoints."""

from rest_framework.routers import SimpleRouter

from platforms.cvecrowd.views import CveCrowdSettingsViewSet

router = SimpleRouter()
router.register("cvecrowd", CveCrowdSettingsViewSet)

urlpatterns = router.urls

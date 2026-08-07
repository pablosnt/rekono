"""URLs of the NVD NIST endpoints."""

from rest_framework.routers import SimpleRouter

from platforms.nvdnist.views import NvdNistSettingsViewSet

router = SimpleRouter()
router.register("nvdnist", NvdNistSettingsViewSet)

urlpatterns = router.urls

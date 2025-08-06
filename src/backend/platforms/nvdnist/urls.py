from rest_framework.routers import SimpleRouter

from platforms.nvdnist.views import NvdNistSettingsViewSet

router = SimpleRouter()
router.register("nvdnist", NvdNistSettingsViewSet)

urlpatterns = router.urls

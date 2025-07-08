from rest_framework.routers import SimpleRouter

from platforms.nvdnist.views import NvdNistSettingsViewSet

# Register your views here.

router = SimpleRouter()
router.register("nvdnist", NvdNistSettingsViewSet)

urlpatterns = router.urls

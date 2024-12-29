from platforms.nvdnist.views import NvdNistSettingsViewSet
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register("nvdnist", NvdNistSettingsViewSet)

urlpatterns = router.urls

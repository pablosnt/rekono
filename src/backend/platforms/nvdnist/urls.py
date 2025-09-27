"""URL routing configuration for NVD NIST platform API endpoints.

Defines URL patterns and routing for NVD NIST platform REST API endpoints
using Django REST framework router configuration.
"""

from rest_framework.routers import SimpleRouter

from platforms.nvdnist.views import NvdNistSettingsViewSet

router = SimpleRouter()
router.register("nvdnist", NvdNistSettingsViewSet)

urlpatterns = router.urls

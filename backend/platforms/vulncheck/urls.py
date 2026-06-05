"""URL routing configuration for VulnCheck platform API endpoints.

Defines URL patterns and routing for VulnCheck platform REST API endpoints
using Django REST framework router configuration.
"""

from rest_framework.routers import SimpleRouter

from platforms.vulncheck.views import VulnCheckSettingsViewSet

router = SimpleRouter()
router.register("vulncheck", VulnCheckSettingsViewSet)

urlpatterns = router.urls

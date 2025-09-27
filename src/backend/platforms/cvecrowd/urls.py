"""URL routing configuration for CVE Crowd platform API endpoints.

Configures REST API URL patterns for CVE Crowd platform management operations
using Django REST framework routers for automated endpoint generation.
"""

from rest_framework.routers import SimpleRouter

from platforms.cvecrowd.views import CveCrowdSettingsViewSet

router = SimpleRouter()
router.register("cvecrowd", CveCrowdSettingsViewSet)

urlpatterns = router.urls

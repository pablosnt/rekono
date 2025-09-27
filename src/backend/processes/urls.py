"""URL routing configuration for process management API endpoints.

Configures REST API URL patterns for process and step management operations
using Django REST framework routers for automated endpoint generation.
"""

from rest_framework.routers import SimpleRouter

from processes.views import ProcessViewSet, StepViewSet

router = SimpleRouter()
router.register("processes", ProcessViewSet)
router.register("steps", StepViewSet)

urlpatterns = router.urls

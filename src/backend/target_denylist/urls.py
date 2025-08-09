"""URL routing configuration for target denylist API endpoints.

Defines URL patterns and routing for target denylist REST API endpoints
using Django REST Framework's SimpleRouter for standard CRUD operations.
"""

from rest_framework.routers import SimpleRouter

from target_denylist.views import TargetDenylistViewSet

router = SimpleRouter()
router.register("target-denylist", TargetDenylistViewSet)

urlpatterns = router.urls

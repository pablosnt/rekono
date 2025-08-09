"""URL configuration for target ports REST API.

Defines URL routing for target port endpoints using Django REST framework
router with the TargetPortViewSet for API operations.
"""

from rest_framework.routers import SimpleRouter

from target_ports.views import TargetPortViewSet

router = SimpleRouter()
router.register("target-ports", TargetPortViewSet)

urlpatterns = router.urls

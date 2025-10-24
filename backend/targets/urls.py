"""URL configuration for targets REST API.

Defines URL routing for target endpoints using Django REST framework
router with the TargetViewSet for API operations.
"""

from rest_framework.routers import SimpleRouter

from targets.views import TargetViewSet

router = SimpleRouter()
router.register("targets", TargetViewSet)

urlpatterns = router.urls

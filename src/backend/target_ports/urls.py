from rest_framework.routers import SimpleRouter

from target_ports.views import TargetPortViewSet

router = SimpleRouter()
router.register("target-ports", TargetPortViewSet)

urlpatterns = router.urls

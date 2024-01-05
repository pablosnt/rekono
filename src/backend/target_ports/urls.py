from rest_framework.routers import SimpleRouter

from target_ports.views import TargetPortViewSet

# Register your views here.

router = SimpleRouter()
router.register("target-ports", TargetPortViewSet)

urlpatterns = router.urls

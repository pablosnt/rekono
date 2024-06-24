from rest_framework.routers import SimpleRouter
from target_denylist.views import TargetDenylistViewSet

# Register your views here.

router = SimpleRouter()
router.register("target-denylist", TargetDenylistViewSet)

urlpatterns = router.urls

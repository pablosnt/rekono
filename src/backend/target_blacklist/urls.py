from rest_framework.routers import SimpleRouter
from target_blacklist.views import TargetBlacklistViewSet

# Register your views here.

router = SimpleRouter()
router.register("target-blacklist", TargetBlacklistViewSet)

urlpatterns = router.urls

from rest_framework.routers import SimpleRouter
from targets.views import TargetViewSet

# Register your views here.

router = SimpleRouter()
router.register("targets", TargetViewSet)

urlpatterns = router.urls

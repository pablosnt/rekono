from rest_framework.routers import SimpleRouter

from targets.views import TargetPortViewSet, TargetViewSet

# Register your views here.

router = SimpleRouter()
router.register('targets', TargetViewSet)
router.register('target-ports', TargetPortViewSet)

urlpatterns = router.urls

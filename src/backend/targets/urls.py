from rest_framework.routers import SimpleRouter

from targets.views import TargetViewSet

router = SimpleRouter()
router.register("targets", TargetViewSet)

urlpatterns = router.urls

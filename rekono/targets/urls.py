from targets.views import TargetViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('targets', TargetViewSet)

urlpatterns = router.urls

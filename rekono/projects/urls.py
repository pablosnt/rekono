from projects.views import ProjectViewSet, TargetViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('projects', ProjectViewSet)
router.register('targets', TargetViewSet)

urlpatterns = router.urls

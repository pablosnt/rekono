from rest_framework.routers import SimpleRouter
from projects.views import ProjectViewSet, TargetViewSet

router = SimpleRouter()
router.register('projects', ProjectViewSet)
router.register('targets', TargetViewSet)

urlpatterns = router.urls

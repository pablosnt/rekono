from projects.views import ProjectViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('projects', ProjectViewSet)

urlpatterns = router.urls

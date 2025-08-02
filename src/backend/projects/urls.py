from rest_framework.routers import SimpleRouter

from projects.views import ProjectViewSet

router = SimpleRouter()
router.register("projects", ProjectViewSet)

urlpatterns = router.urls

from rest_framework.routers import SimpleRouter

from projects.views import ProjectViewSet

# Register your views here.

router = SimpleRouter()
router.register("projects", ProjectViewSet)

urlpatterns = router.urls

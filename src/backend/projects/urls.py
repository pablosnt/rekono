from projects.views import ProjectViewSet
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register('projects', ProjectViewSet)

urlpatterns = router.urls

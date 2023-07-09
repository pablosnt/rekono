from rest_framework.routers import SimpleRouter
from tools.views import ConfigurationViewSet, ToolViewSet

# Register your views here.

router = SimpleRouter()
router.register('tools', ToolViewSet)
router.register('configurations', ConfigurationViewSet)

urlpatterns = router.urls

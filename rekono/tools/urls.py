from tools.views import ToolViewSet
from tools.views import ConfigurationViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('tools', ToolViewSet)
router.register('configurations', ConfigurationViewSet)

urlpatterns = router.urls

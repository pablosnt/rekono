"""URLs of the tool endpoints."""

from rest_framework.routers import SimpleRouter

from tools.views import ConfigurationViewSet, ToolViewSet

router = SimpleRouter()
router.register("tools", ToolViewSet)
router.register("configurations", ConfigurationViewSet)

urlpatterns = router.urls

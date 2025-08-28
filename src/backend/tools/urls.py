"""URL configuration for tools module API endpoints.

Configures REST API routing for tools and configurations endpoints
using Django REST framework's SimpleRouter.
"""

from rest_framework.routers import SimpleRouter

from tools.views import ConfigurationViewSet, ToolViewSet

router = SimpleRouter()
router.register("tools", ToolViewSet)
router.register("configurations", ConfigurationViewSet)

urlpatterns = router.urls

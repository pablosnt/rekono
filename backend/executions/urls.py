"""URLs of the execution endpoints."""

from rest_framework.routers import SimpleRouter

from executions.views import ExecutionViewSet

router = SimpleRouter()
router.register("executions", ExecutionViewSet)

urlpatterns = router.urls

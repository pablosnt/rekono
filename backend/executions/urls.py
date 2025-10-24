"""URL configuration for execution API endpoints.

Defines URL routing for execution REST API endpoints including
execution records and report download functionality.
"""

from rest_framework.routers import SimpleRouter

from executions.views import ExecutionViewSet

router = SimpleRouter()
router.register("executions", ExecutionViewSet)

urlpatterns = router.urls

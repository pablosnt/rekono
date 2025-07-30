"""URL configuration for execution API endpoints.

This module defines the URL routing for execution-related REST API
endpoints, providing access to execution records and report downloads.
"""

from rest_framework.routers import SimpleRouter

from executions.views import ExecutionViewSet

router = SimpleRouter()
router.register("executions", ExecutionViewSet)

urlpatterns = router.urls

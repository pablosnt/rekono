"""URL configuration for task API endpoints.

Defines URL routing for task-related REST API endpoints using
Django REST framework's SimpleRouter.
"""

from rest_framework.routers import SimpleRouter

from tasks.views import LatestTasksViewSet, TaskViewSet

router = SimpleRouter()
router.register("tasks/latest", LatestTasksViewSet, basename="latest-tasks")
router.register("tasks", TaskViewSet)

urlpatterns = router.urls

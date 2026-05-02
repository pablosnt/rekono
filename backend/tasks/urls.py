"""URL configuration for task API endpoints.

Defines URL routing for task-related REST API endpoints using
Django REST framework's SimpleRouter.
"""

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from tasks.views import LatestTasksViewSet, TaskViewSet

router = SimpleRouter()
router.register("tasks", TaskViewSet)

urlpatterns = [
    path("tasks/latest/", LatestTasksViewSet.as_view({"get": "list"}), name="latest-tasks"),
    path("", include(router.urls)),
]

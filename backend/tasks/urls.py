"""URLs of the task endpoints."""

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from tasks.views import LatestTasksViewSet, TaskViewSet

router = SimpleRouter()
router.register("tasks", TaskViewSet)

urlpatterns = [
    path("tasks/latest/", LatestTasksViewSet.as_view({"get": "list"}), name="latest-tasks"),
    path("", include(router.urls)),
]

"""URLs of the project endpoints."""

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from projects.views import ProjectViewSet, TopProjectsViewSet

router = SimpleRouter()
router.register("projects", ProjectViewSet)

urlpatterns = [
    path("projects/top/", TopProjectsViewSet.as_view({"get": "list"}), name="top-projects"),
    path("", include(router.urls)),
]

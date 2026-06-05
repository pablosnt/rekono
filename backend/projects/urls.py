"""URL routing configuration for project REST API endpoints.

Defines URL patterns and routing for project-related API endpoints using
Django REST framework's SimpleRouter for automated REST API URL generation.
"""

from django.urls import include, path
from rest_framework.routers import SimpleRouter

from projects.views import ProjectViewSet, TopProjectsViewSet

router = SimpleRouter()
router.register("projects", ProjectViewSet)

urlpatterns = [
    path("projects/top/", TopProjectsViewSet.as_view({"get": "list"}), name="top-projects"),
    path("", include(router.urls)),
]

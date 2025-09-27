"""URL configuration for notes REST API endpoints.

Defines URL patterns for note management API using Django REST framework
router to register ViewSet endpoints for note operations and collaboration features.
"""

from rest_framework.routers import SimpleRouter

from notes.views import NoteViewSet

router = SimpleRouter()
router.register("notes", NoteViewSet)

urlpatterns = router.urls

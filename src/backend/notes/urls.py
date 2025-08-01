"""URL routing configuration for the notes app.

This module defines the URL patterns for the notes app, providing
API endpoints for note management and forking functionality.
"""

from rest_framework.routers import SimpleRouter

from notes.views import NoteViewSet

router = SimpleRouter()
router.register("notes", NoteViewSet)

urlpatterns = router.urls

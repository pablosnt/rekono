from rest_framework.routers import SimpleRouter
from notes.views import NoteViewSet

router = SimpleRouter()
router.register("notes", NoteViewSet)

urlpatterns = router.urls

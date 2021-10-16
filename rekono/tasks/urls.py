from rest_framework.routers import SimpleRouter
from tasks.views import TaskViewSet

router = SimpleRouter()
router.register('tasks', TaskViewSet)

urlpatterns = router.urls

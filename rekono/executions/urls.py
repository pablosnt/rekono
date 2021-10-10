from executions.views import ExecutionViewSet, TaskViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('tasks', TaskViewSet)
router.register('executions', ExecutionViewSet)

urlpatterns = router.urls

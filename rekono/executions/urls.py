from executions.views import ExecutionViewSet, RequestViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('requests', RequestViewSet)
router.register('executions', ExecutionViewSet)

urlpatterns = router.urls

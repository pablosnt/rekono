from executions.views import ExecutionViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('executions', ExecutionViewSet)

urlpatterns = router.urls

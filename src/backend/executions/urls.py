from executions.views import ExecutionViewSet
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register('executions', ExecutionViewSet)

urlpatterns = router.urls

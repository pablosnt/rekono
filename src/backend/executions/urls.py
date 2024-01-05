from rest_framework.routers import SimpleRouter

from executions.views import ExecutionViewSet

# Register your views here.

router = SimpleRouter()
router.register("executions", ExecutionViewSet)

urlpatterns = router.urls

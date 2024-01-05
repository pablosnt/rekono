from rest_framework.routers import SimpleRouter

from processes.views import ProcessViewSet, StepViewSet

# Register your views here.

router = SimpleRouter()
router.register("processes", ProcessViewSet)
router.register("steps", StepViewSet)

urlpatterns = router.urls

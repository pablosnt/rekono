from processes.views import ProcessViewSet, StepViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('processes', ProcessViewSet)
router.register('steps', StepViewSet)

urlpatterns = router.urls

from rest_framework.routers import SimpleRouter
from processes.views import ProcessViewSet

router = SimpleRouter()
router.register('processes', ProcessViewSet)

urlpatterns = router.urls

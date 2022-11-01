from rest_framework.routers import SimpleRouter

from system.views import SystemViewSet

# Register your views here.

router = SimpleRouter()
router.register('system', SystemViewSet)

urlpatterns = router.urls

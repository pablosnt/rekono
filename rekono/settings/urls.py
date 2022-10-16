from rest_framework.routers import SimpleRouter

from settings.views import SettingViewSet

# Register your views here.

router = SimpleRouter()
router.register('settings', SettingViewSet)

urlpatterns = router.urls

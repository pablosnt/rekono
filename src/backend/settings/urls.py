from rest_framework.routers import SimpleRouter
from settings.views import SettingsViewSet

# Register your views here.

router = SimpleRouter()
router.register("settings", SettingsViewSet)

urlpatterns = router.urls

from platforms.mail.views import SMTPSettingsViewSet
from rest_framework.routers import SimpleRouter

# Register your views here.

router = SimpleRouter()
router.register("smtp/settings", SMTPSettingsViewSet)

urlpatterns = router.urls
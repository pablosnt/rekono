from rest_framework.routers import SimpleRouter

from platforms.mail.views import SMTPSettingsViewSet

# Register your views here.

router = SimpleRouter()
router.register("smtp", SMTPSettingsViewSet)

urlpatterns = router.urls

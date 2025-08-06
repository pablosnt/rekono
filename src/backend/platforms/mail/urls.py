from rest_framework.routers import SimpleRouter

from platforms.mail.views import SMTPSettingsViewSet

router = SimpleRouter()
router.register("smtp", SMTPSettingsViewSet)

urlpatterns = router.urls

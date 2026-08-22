"""URLs of the SMTP endpoints."""

from rest_framework.routers import SimpleRouter

from platforms.email.views import SMTPSettingsViewSet

router = SimpleRouter()
router.register("smtp", SMTPSettingsViewSet)

urlpatterns = router.urls

"""URLs of the VulnCheck endpoints."""

from rest_framework.routers import SimpleRouter

from platforms.vulncheck.views import VulnCheckSettingsViewSet

router = SimpleRouter()
router.register("vulncheck", VulnCheckSettingsViewSet)

urlpatterns = router.urls

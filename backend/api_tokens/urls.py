"""URLs of the API token endpoints."""

from rest_framework.routers import SimpleRouter

from api_tokens.views import ApiTokenViewSet

router = SimpleRouter()
router.register("api-tokens", ApiTokenViewSet)

urlpatterns = router.urls

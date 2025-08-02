"""URL routing for API token endpoints.

Defines URL patterns for API token REST endpoints including
CRUD operations for user API token management.
"""

from rest_framework.routers import SimpleRouter

from api_tokens.views import ApiTokenViewSet

router = SimpleRouter()
router.register("api-tokens", ApiTokenViewSet)

urlpatterns = router.urls

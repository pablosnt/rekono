"""URL routing configuration for the integrations app.

This module defines the URL patterns for the integrations app, providing
API endpoints for integration management and configuration.
"""

from rest_framework.routers import SimpleRouter

from integrations.views import IntegrationViewSet

router = SimpleRouter()
router.register("integrations", IntegrationViewSet)

urlpatterns = router.urls

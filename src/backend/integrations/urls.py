"""URL configuration for integrations REST API endpoints.

Defines URL patterns for integration management API using Django REST framework
router to register ViewSet endpoints for integration operations.
"""

from rest_framework.routers import SimpleRouter

from integrations.views import IntegrationViewSet

router = SimpleRouter()
router.register("integrations", IntegrationViewSet)

urlpatterns = router.urls

"""URL configuration for integrations REST API endpoints.

Registers the "integrations" endpoint with Django REST framework's SimpleRouter,
routing requests to IntegrationViewSet for third-party integration management.
"""

from rest_framework.routers import SimpleRouter

from integrations.views import IntegrationViewSet

router = SimpleRouter()
router.register("integrations", IntegrationViewSet)

urlpatterns = router.urls


from rest_framework.routers import SimpleRouter

from integrations.views import IntegrationViewSet

router = SimpleRouter()
router.register("integrations", IntegrationViewSet)

urlpatterns = router.urls

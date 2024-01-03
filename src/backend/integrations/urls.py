from rest_framework.routers import SimpleRouter
from integrations.views import IntegrationViewSet

# Register your views here.

router = SimpleRouter()
router.register("integrations", IntegrationViewSet)

urlpatterns = router.urls

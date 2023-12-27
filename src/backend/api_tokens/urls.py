from api_tokens.views import ApiTokenViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("api-tokens", ApiTokenViewSet)

urlpatterns = router.urls

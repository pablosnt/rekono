from http_headers.views import HttpHeaderViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("http-headers", HttpHeaderViewSet)

urlpatterns = router.urls

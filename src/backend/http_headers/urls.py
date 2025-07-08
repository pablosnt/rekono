from rest_framework.routers import SimpleRouter

from http_headers.views import HttpHeaderViewSet

router = SimpleRouter()
router.register("http-headers", HttpHeaderViewSet)

urlpatterns = router.urls

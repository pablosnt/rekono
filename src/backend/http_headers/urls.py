"""URL routing configuration for HTTP headers API endpoints.

Provides RESTful URL patterns for HTTP header management
operations through the Django REST framework router.
"""

from rest_framework.routers import SimpleRouter

from http_headers.views import HttpHeaderViewSet

router = SimpleRouter()
router.register("http-headers", HttpHeaderViewSet)

urlpatterns = router.urls

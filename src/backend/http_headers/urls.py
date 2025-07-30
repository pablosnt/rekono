"""URL configuration for HTTP header API endpoints.

This module defines the URL routing for HTTP header-related REST API
endpoints, providing CRUD operations for HTTP header records.
"""

from rest_framework.routers import SimpleRouter

from http_headers.views import HttpHeaderViewSet

router = SimpleRouter()
router.register("http-headers", HttpHeaderViewSet)

urlpatterns = router.urls

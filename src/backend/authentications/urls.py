"""URL configuration for authentication API endpoints.

This module defines the URL routing for authentication-related REST API
endpoints, providing CRUD operations for authentication records.
"""

from rest_framework.routers import SimpleRouter

from authentications.views import AuthenticationViewSet

router = SimpleRouter()
router.register("authentications", AuthenticationViewSet)

urlpatterns = router.urls

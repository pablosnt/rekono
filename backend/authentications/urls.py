"""URL configuration for authentication API endpoints.

Defines URL routing for authentication REST API endpoints with
CRUD operations for authentication records.
"""

from rest_framework.routers import SimpleRouter

from authentications.views import AuthenticationViewSet

router = SimpleRouter()
router.register("authentications", AuthenticationViewSet)

urlpatterns = router.urls

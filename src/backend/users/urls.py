from django.urls import include, path
from rest_framework.routers import SimpleRouter

from users.views import MfaViewSet, ProfileViewSet, UserViewSet

router = SimpleRouter()
router.register("users", UserViewSet)
router.register("profile/mfa", MfaViewSet, basename="mfa")

urlpatterns = [
    path("profile/", ProfileViewSet.as_view({"get": "get_profile", "put": "update_profile"})),
    path("profile/update-password/", ProfileViewSet.as_view({"put": "update_password"})),
    path("", include(router.urls)),
]

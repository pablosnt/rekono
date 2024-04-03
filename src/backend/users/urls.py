from django.urls import include, path
from rest_framework.routers import SimpleRouter
from users.views import (
    CreateUserViewSet,
    MfaViewSet,
    ProfileViewSet,
    ResetPasswordViewSet,
    UserViewSet,
)

# Register your views here.

router = SimpleRouter()
router.register("users", UserViewSet)
router.register("users/create", CreateUserViewSet)
router.register("profile/mfa", MfaViewSet)
router.register("security", ResetPasswordViewSet)

urlpatterns = [
    path(
        "profile/",
        ProfileViewSet.as_view({"get": "get_profile", "put": "update_profile"}),
    ),
    path(
        "profile/update-password/", ProfileViewSet.as_view({"put": "update_password"})
    ),
    path("", include(router.urls)),
]

from django.urls import include, path
from rest_framework.routers import SimpleRouter
from users.views import (
    CreateUserViewSet,
    ProfileViewSet,
    ResetPasswordViewSet,
    UserViewSet,
)

# Register your views here.

router = SimpleRouter()
router.register("users", UserViewSet)
# router.register("users/create", CreateUserViewSet)

urlpatterns = [
    path("users/create/", CreateUserViewSet.as_view({"post": "create"})),
    path("profile/", ProfileViewSet.as_view({"get": "get", "put": "update"})),
    path(
        "security/update-password/", ProfileViewSet.as_view({"put": "update_password"})
    ),
    path(
        "security/reset-password/",
        ResetPasswordViewSet.as_view({"post": "create", "put": "update"}),
    ),
    path("", include(router.urls)),
]

from django.urls import include, path
from rest_framework.routers import SimpleRouter
from security.authentication.views import (
    LoginViewSet,
    LogoutViewSet,
    RefreshTokenViewSet,
)

# Register your views here.

router = SimpleRouter()
router.register("security/logout", LogoutViewSet, basename="logout")

urlpatterns = [
    path("security/login/", LoginViewSet.as_view(), name="login"),
    path(
        "security/refresh-token/", RefreshTokenViewSet.as_view(), name="refresh-token"
    ),
    path("", include(router.urls)),
]

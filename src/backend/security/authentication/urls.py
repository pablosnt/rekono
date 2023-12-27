from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from security.authentication.views import LoginViewSet, RefreshTokenViewSet

# Register your views here.

urlpatterns = [
    path("security/login/", LoginViewSet.as_view(), name="login"),
    path(
        "security/refresh-token/", RefreshTokenViewSet.as_view(), name="refresh-token"
    ),
    path("security/logout/", TokenBlacklistView.as_view(), name="logout"),
]

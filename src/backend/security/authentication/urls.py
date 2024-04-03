from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from security.authentication.views import (
    LoginView,
    MfaLoginView,
    RefreshTokenViewSet,
    SendEmailMfaView,
)

urlpatterns = [
    path("security/login/", LoginView.as_view(), name="login"),
    path(
        "security/refresh-token/", RefreshTokenViewSet.as_view(), name="refresh-token"
    ),
    path("security/mfa/", MfaLoginView.as_view(), name="mfa"),
    path("security/mfa/email/", SendEmailMfaView.as_view(), name="send-email-mfa"),
    path("security/logout/", TokenBlacklistView.as_view(), name="logout"),
]

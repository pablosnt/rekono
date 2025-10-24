"""URL configuration for authentication endpoints.

Defines URL patterns for authentication-related API endpoints including
login, logout, token refresh, and multi-factor authentication flows.
These endpoints provide the complete authentication API for the Rekono platform.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView

from security.authentication.views import LoginView, MfaLoginView, RefreshTokenViewSet, SendEmailMfaView

urlpatterns = [
    path("security/login/", LoginView.as_view(), name="login"),
    path("security/refresh/", RefreshTokenViewSet.as_view(), name="refresh"),
    path("security/mfa/", MfaLoginView.as_view(), name="mfa"),
    path("security/mfa/email/", SendEmailMfaView.as_view(), name="send-email-mfa"),
    path("security/logout/", TokenBlacklistView.as_view(), name="logout"),
]

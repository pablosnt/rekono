"""URLs of the authentication endpoints: login, MFA, token refresh, and logout.

They are registered with plain Django ``path()`` calls rather than a DRF router,
since each endpoint is a single-purpose view rather than a CRUD resource.
"""

from django.urls import path

from security.authentication.views import LoginView, LogoutView, MfaLoginView, RefreshTokenViewSet, SendEmailMfaView

urlpatterns = [
    path("security/login/", LoginView.as_view(), name="login"),
    path("security/refresh/", RefreshTokenViewSet.as_view(), name="refresh"),
    path("security/mfa/", MfaLoginView.as_view(), name="mfa"),
    path("security/mfa/email/", SendEmailMfaView.as_view(), name="send-email-mfa"),
    path("security/logout/", LogoutView.as_view(), name="logout"),
]

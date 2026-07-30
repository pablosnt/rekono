"""Custom JWT token class for multi-factor authentication workflows.

Provides the MfaRequiredToken class, a limited-scope JWT issued after primary
credential validation but before MFA completion. It bridges the gap between
login and MFA completion without granting access to the rest of the API.
"""

from rest_framework_simplejwt.tokens import BlacklistMixin, Token

from rekono.settings import SIMPLE_JWT


class MfaRequiredToken(BlacklistMixin, Token):
    """Temporary JWT token for MFA completion requirements.

    A specialized JWT token issued after successful primary authentication
    (username/password) but before MFA completion. Its token_type ("mfa_required")
    differs from the access token type, so the standard JWT authentication backend
    rejects it and it cannot be used to reach the rest of the API.

    Security Features:
        - Short-lived, matching the access token lifetime, to minimize the exposure window
        - Rejected by the standard JWT authentication backend due to its distinct token type
        - Blacklisted by the MFA login flow once the MFA code is verified, so it cannot be reused
        - A full access/refresh token pair is only issued after the MFA challenge succeeds

    Attributes:
        token_type (str): Identifier for this token type ("mfa_required").
        lifetime (timedelta): Token lifetime, matching the access token lifetime.
    """

    token_type = "mfa_required"
    lifetime = SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]

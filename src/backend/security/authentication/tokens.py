"""Custom JWT token classes for multi-factor authentication workflows.

Provides specialized JWT token classes for handling multi-factor authentication
requirements. These tokens have limited scope and are used to bridge the gap
between initial credential validation and MFA completion.
"""

from rest_framework_simplejwt.tokens import BlacklistMixin, Token

from rekono.settings import SIMPLE_JWT


class MfaRequiredToken(BlacklistMixin, Token):
    """Temporary JWT token for MFA completion requirements.

    A specialized JWT token issued after successful primary authentication
    (username/password) but before MFA completion. This token has limited
    scope and can only be used to access MFA completion endpoints.

    Features:
        - Limited lifetime matching access tokens
        - Automatic blacklisting support for security
        - Restricted scope for MFA completion only
        - Integration with JWT authentication framework

    Security:
        - Short-lived to minimize exposure window
        - Single-use enforcement through blacklisting
        - Cannot be used for general API access
        - Requires completion of MFA challenge for full tokens

    Attributes:
        token_type (str): Identifier for this token type ("mfa_required").
        lifetime (timedelta): Token lifetime from JWT configuration.
    """

    token_type = "mfa_required"
    lifetime = SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]

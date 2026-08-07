"""Token that links the two steps of a login that requires MFA."""

from rest_framework_simplejwt.tokens import BlacklistMixin, Token

from rekono.settings import SIMPLE_JWT


class MfaRequiredToken(BlacklistMixin, Token):
    """Temporary token issued after the password, while the MFA code is missing.

    Its token type differs from the one of the access tokens, so the standard JWT
    authentication backend rejects it and it can only be used to complete the MFA
    login, which blacklists it as soon as the code is verified.

    Attributes:
        token_type: Type that distinguishes these tokens from the access ones.
        lifetime: Same lifetime as the access tokens, to keep the login short.
    """

    token_type = "mfa_required"
    lifetime = SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]

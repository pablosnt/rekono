from rekono.settings import SIMPLE_JWT
from rest_framework_simplejwt.tokens import BlacklistMixin, Token


class MfaRequiredToken(BlacklistMixin, Token):
    token_type = "mfa_required"
    lifetime = SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]

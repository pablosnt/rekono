"""OpenAPI schema extensions for the Rekono authentication backends.

The extensions are discovered automatically once this module is imported, which
happens inside SecurityConfig.ready() to guarantee that the app registry is fully
loaded first.
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """Description of the cookie-aware JWT backend as a Bearer security scheme.

    Without this extension, drf-spectacular can't resolve the authenticator and
    omits the security requirement from every endpoint that uses it.

    Attributes:
        target_class: Import path of the authentication backend it describes.
        name: Name of the security scheme in the OpenAPI components section.
    """

    target_class = "security.authentication.jwt.CookieJWTAuthentication"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        """Return the OpenAPI security scheme object for the JWT Bearer tokens.

        Args:
            auto_schema: Schema generator that requests the definition, not needed
              here because the scheme is the same for every endpoint.
        """
        from rest_framework_simplejwt.settings import api_settings

        return build_bearer_security_scheme_object(
            header_name=getattr(api_settings, "AUTH_HEADER_NAME", "HTTP_AUTHORIZATION"),
            token_prefix=api_settings.AUTH_HEADER_TYPES[0],
            bearer_format="JWT",
        )

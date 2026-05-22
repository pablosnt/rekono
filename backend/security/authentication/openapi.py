"""OpenAPI schema extensions for Rekono authentication backends.

Registers drf-spectacular extensions so that custom authentication classes
are correctly described in the generated OpenAPI schema. Each extension is
discovered automatically once this module is imported, which happens inside
SecurityConfig.ready() to guarantee the app registry is fully loaded first.
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """OpenAPI extension for CookieJWTAuthentication.

    Maps the cookie-aware JWT backend to the standard Bearer security scheme
    so drf-spectacular can include it in the generated OpenAPI spec. Without
    this extension, drf-spectacular cannot resolve the authenticator and omits
    the security requirement from every endpoint that uses it.

    Attributes:
        target_class (str): Fully-qualified import path of the authenticator.
        name (str): Security scheme name used in the OpenAPI components section.
    """

    target_class = "security.authentication.jwt.CookieJWTAuthentication"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        """Return the OpenAPI security scheme object for JWT Bearer auth.

        Args:
            auto_schema: The drf-spectacular AutoSchema instance.

        Returns:
            dict: An OpenAPI 3.0 Bearer security scheme object.
        """
        from rest_framework_simplejwt.settings import api_settings

        return build_bearer_security_scheme_object(
            header_name=getattr(api_settings, "AUTH_HEADER_NAME", "HTTP_AUTHORIZATION"),
            token_prefix=api_settings.AUTH_HEADER_TYPES[0],
            bearer_format="JWT",
        )

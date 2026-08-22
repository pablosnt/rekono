"""Middleware that applies the HTTP security controls of Rekono.

Adds the security headers, including the Content Security Policy of each path and
the CORS headers, resolves the real client IP address behind the trusted proxies,
and logs every request with its response.
"""

from dataclasses import dataclass
from typing import Any

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework.throttling import BaseThrottle

from framework.context import RequestContext
from framework.logging import LoggingEntity
from rekono.settings import CONFIG

# Maps request path prefixes to the Content-Security-Policy applied to matching responses.
# Matching is first-prefix-wins in insertion order, so the more specific /api/schema/... entries
# must stay ahead of the general /api/ entry, which would otherwise shadow them.
CSP = {
    "/admin": "; ".join(
        [
            "default-src 'none'",
            "connect-src 'self'",
            "base-uri 'none'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "script-src 'self'",
            "style-src 'self' ",
            "img-src 'self'",
            "font-src 'self'",
        ]
    ),
    "/api/schema/swagger-ui": "; ".join(
        [
            "default-src 'none'",
            "base-uri 'none'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            # 'unsafe-inline' required due to an inline script with hardcoded dynamic CSRF token, so its hash changes
            "script-src cdn.jsdelivr.net 'unsafe-inline'",
            "style-src cdn.jsdelivr.net fonts.googleapis.com 'sha256-MMpT0iDxyjALd9PdfepImGX3DBfJPXZ4IlDWdPAgtn0='",
            "img-src data: cdn.jsdelivr.net",
            "connect-src 'self' cdn.jsdelivr.net",
        ]
    ),
    "/api/schema/redoc": "; ".join(
        [
            "default-src 'none'",
            "base-uri 'none'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "script-src cdn.jsdelivr.net",
            "style-src cdn.jsdelivr.net fonts.googleapis.com 'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=' 'sha256-QMIg+bpjm3JdElJ388KYke01izlUW0UoNOeKjpMxdgc=' 'sha256-GvZq6XrzMRhFZ2MvEI09Lw7QbE3DnWuVQTMYafGYLcg='",
            "img-src 'self' data: cdn.jsdelivr.net cdn.redoc.ly",
            "font-src fonts.gstatic.com",
            "worker-src blob:",
            "child-src blob:",
            "connect-src 'self' cdn.jsdelivr.net",
        ]
    ),
    "/api/": "; ".join(["default-src 'none'", "base-uri 'none'", "object-src 'none'", "frame-ancestors 'none'"]),
}
# Headers applied to every response, where None means that _add_security_headers resolves
# the value per request. A None that survives it is sent as the literal string "None",
# which is what hides the real server behind the Server header, and what a path matching
# no CSP prefix gets.
SECURITY_HEADERS = {
    "Content-Security-Policy": None,
    "Server": None,
    "Cache-Control": "no-store, no-cache, must-revalidate",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), geolocation=(), microphone=(), midi=(), payment=(), usb=()",
    "Access-Control-Allow-Origin": CONFIG.frontend_origin,
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "content-type, authorization",
    "Access-Control-Allow-Credentials": "true",
}


@dataclass
class SecurityMiddleware(LoggingEntity):
    """Middleware that applies the HTTP security controls to every request.

    It's the first middleware of the chain, so the request context and the client IP
    address are available to the rest of them, and the security headers are applied
    to the responses that they generate.

    Attributes:
        get_response: Next callable of the Django middleware chain.
    """

    get_response: Any

    def _get_options_response(self, request: HttpRequest) -> Response:
        """Build the response for the OPTIONS requests, listing the allowed methods.

        The response is already rendered, since it doesn't go through the view that
        would render it.

        Args:
            request: OPTIONS request being answered.

        Returns:
            An empty 200 response with the Allow header, ready to be sent.
        """
        response = Response(status=status.HTTP_200_OK)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {"request": request, "response": response}
        response = response.render()
        response["Allow"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    def _add_security_headers(self, request: HttpRequest, response: Response) -> Response:
        """Add security headers to an HTTP response before it is returned to the client.

        Applies every entry in SECURITY_HEADERS as-is, except for two that depend on
        the request path. Content-Security-Policy is chosen by matching the path
        against the CSP prefixes. Referrer-Policy relaxes from the default no-referrer
        to strict-origin for paths under /admin, so requests originating from the
        Django admin site still carry their origin.

        Args:
            request: Request whose path decides the resolved values.
            response: Response to be returned, whose headers are set in place.

        Returns:
            The same response, with the security headers already set.
        """
        for header, value in SECURITY_HEADERS.items():
            if header == "Content-Security-Policy":
                for path, csp in CSP.items():
                    if request.path.startswith(path):
                        value = csp
                        break
            elif header == "Referrer-Policy" and request.path.startswith("/admin"):
                value = "strict-origin"  # pragma: no cover
            response[header] = value
        return response

    def _log_request_and_response(self, request: HttpRequest, response: Response):
        """Log a request and its response, using the level that its status deserves.

        Successful requests are logged as information, the ones rejected because of
        a client error as warnings, and the failed ones as errors.

        Args:
            request: Request that was handled.
            response: Response that was generated for it, whose status code decides
              the log level.
        """
        logger_level = self.logger.info
        if response.status_code >= 400 and response.status_code < 500:
            logger_level = self.logger.warning
        elif response.status_code >= 500:  # pragma: no cover
            logger_level = self.logger.error
        logger_level(
            f"{request.method} {request.get_full_path()} > HTTP {response.status_code}",
            extra={"request": request, "response": response},
        )

    def __call__(self, request: HttpRequest) -> Any:
        """Handle one request, applying the security controls to its response.

        The OPTIONS requests are answered here instead of being forwarded to the
        views, and the request is always removed from the context-local storage
        afterwards, even if the request fails, so it isn't reused by the next
        request handled by the same thread.

        Args:
            request: Request to handle, whose REMOTE_ADDR is replaced by the client
              address resolved through the trusted proxies.

        Returns:
            The response of the rest of the chain, with the security headers.
        """
        # DRF resolves the client IP from X-Forwarded-For based on the configured number of trusted
        # proxies, so only the entries appended by them are trusted and the ones supplied by the
        # client are ignored
        request.META["REMOTE_ADDR"] = BaseThrottle().get_ident(request)
        RequestContext.set(request)
        try:
            response = (
                self.get_response(request) if request.method != "OPTIONS" else self._get_options_response(request)
            )
            response = self._add_security_headers(request, response)
            self._log_request_and_response(request, response)
            return response
        finally:
            RequestContext.clear()

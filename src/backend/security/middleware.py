import logging
from dataclasses import dataclass
from typing import Any, Optional

from rekono.settings import CONFIG
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import HttpRequest
from rest_framework.response import Response

logger = logging.getLogger()

CSP = {
    "/admin": (
        "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
        "script-src 'self'; style-src 'self' 'sha256-28J4mQEy4Sqd0R+nZ89dOl9euh+Y3XvT+VfXD5pOiOE='; "
        "img-src 'self'; font-src 'self'"
    ),
    "/api/schema/swagger-ui": (
        "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
        # 'unsafe-inline' required due to a inline script with hardcoded dynamic CSRF token, so its hash changes
        "script-src http://cdn.jsdelivr.net 'unsafe-inline'; "
        "style-src http://cdn.jsdelivr.net fonts.googleapis.com "
        "'sha256-MMpT0iDxyjALd9PdfepImGX3DBfJPXZ4IlDWdPAgtn0='; "
        "img-src data: http://cdn.jsdelivr.net; "
        "connect-src 'self'; "
    ),
    "/api/schema/redoc": (
        "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
        "script-src http://cdn.jsdelivr.net; "
        "style-src http://cdn.jsdelivr.net fonts.googleapis.com "
        "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=' "
        "'sha256-m6OsjZ+ZE+8plS5r0wBVuIy/qbXuHEw//v/OhLyy9Xg=' "
        "'sha256-DLDPR1ic47WIdK2WyeLkblb/tm2mQH+Jt/NNhZWu1k0=' "
        "'sha256-GvZq6XrzMRhFZ2MvEI09Lw7QbE3DnWuVQTMYafGYLcg='; "
        "img-src 'self' data: http://cdn.jsdelivr.net cdn.redoc.ly; "
        "font-src fonts.gstatic.com; "
        "worker-src blob:; "
        "child-src blob:; "
        "connect-src 'self'"
    ),
    "/api/": "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'",
}
SECURITY_HEADERS = {
    "Content-Security-Policy": None,
    "Server": None,
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Access-Control-Allow-Origin": "app://.",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "content-type, authorization",
}


@dataclass
class SecurityMiddleware:
    """Security middleware that manages all HTTP requests and responses."""

    get_response: Any

    def _get_forwarded_address(self, request: HttpRequest) -> Optional[str]:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for and CONFIG.trusted_proxy:
            return x_forwarded_for.split(",", 1)[0]
        return None

    def _http_options(self, request: HttpRequest) -> Response:
        response = Response(status=status.HTTP_200_OK)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {"request": request, "response": response}
        response = response.render()
        response["Allow"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    def _add_security_headers(
        self, request: HttpRequest, response: Response
    ) -> Response:
        for header, value in SECURITY_HEADERS.items():
            if header == "Referrer-Policy" and request.path.startswith("/admin"):
                value = "strict-origin"
            if header == "Content-Security-Policy":
                for path, csp in CSP.items():
                    if request.path.startswith(path):
                        value = csp
                        break
            response[header] = value
        return response

    def _log_request_and_response(self, request: HttpRequest, response: Response):
        logger_level = logger.info
        if response.status_code >= 400 and response.status_code < 500:
            logger_level = logger.warning  # Warning level for 4XX error responses
        elif response.status_code >= 500:  # pragma: no cover
            logger_level = logger.error  # Error level for 5XX error responses
        logger_level(
            f"{request.method} {request.get_full_path()} > HTTP {response.status_code}",
            extra={"request": request, "response": response},
        )

    def __call__(self, request: HttpRequest) -> Any:
        """Process HTTP requests when received and return HTTP responses.

        Args:
            request (HttpRequest): HTTP request

        Returns:
            Any: HTTP response
        """
        forwarded_address = self._get_forwarded_address(request)
        if forwarded_address:
            request.META["REMOTE_ADDR"] = forwarded_address
        response = (
            self.get_response(request)
            if request.method != "OPTIONS"
            else self._http_options(request)
        )
        response = self._add_security_headers(request, response)
        self._log_request_and_response(request, response)
        return response

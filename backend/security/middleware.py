"""Security middleware for HTTP request/response processing in Rekono.

Provides comprehensive security controls for HTTP traffic including security headers,
Content Security Policy (CSP) configuration, CORS handling, and request/response
logging. This middleware implements defense-in-depth security measures to protect
against common web application attacks.
"""

from dataclasses import dataclass
from typing import Any

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import HttpRequest
from rest_framework.response import Response

from framework.context import RequestContext
from framework.logging import LoggingEntity
from rekono.settings import CONFIG

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
            # 'unsafe-inline' required due to a inline script with hardcoded dynamic CSRF token, so its hash changes
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
SECURITY_HEADERS = {
    "Content-Security-Policy": None,
    "Server": None,
    "Cache-Control": "no-store, no-cache, must-revalidate",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), geolocation=(), microphone=(), midi=(), payment=(), usb=()",
    "Access-Control-Allow-Origin": None,
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "content-type, authorization",
    "Access-Control-Allow-Credentials": "true",
}


@dataclass
class SecurityMiddleware(LoggingEntity):
    """Django security middleware providing comprehensive HTTP security controls.

    Implements defense-in-depth security measures for HTTP requests and responses
    including security headers, Content Security Policy enforcement, CORS handling,
    and comprehensive request/response logging for security monitoring.

    Security Controls:
        - Path-specific Content Security Policy (CSP) enforcement
        - Comprehensive security headers to prevent common attacks
        - Custom OPTIONS responses
        - Request/response logging with status code-based log levels
        - Trusted proxy support for accurate client IP identification

    Attributes:
        get_response (Any): Django middleware callable for processing requests.

    Example:
        Configure in Django settings MIDDLEWARE:

        ```python
        MIDDLEWARE = [
            'security.middleware.SecurityMiddleware',
            # ... other middleware
        ]
        ```
    """

    get_response: Any

    def _get_source_ip_address(self, request: HttpRequest) -> str:
        """Extract the real client IP address from request headers.

        Determines the actual client IP address by checking X-Forwarded-For
        headers when behind trusted proxies, falling back to REMOTE_ADDR
        for direct connections. This ensures accurate IP logging and
        security monitoring.

        Args:
            request (HttpRequest): Django HTTP request object.

        Returns:
            str: The client's IP address.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for and CONFIG.trusted_proxy:
            return x_forwarded_for.split(",", 1)[0]  # pragma: no cover
        return request.META["REMOTE_ADDR"]

    def _get_options_response(self, request: HttpRequest) -> Response:
        """Generate HTTP OPTIONS response.

        Creates a proper HTTP response for OPTIONS requests
        with appropriate Allow headers and JSON content type.

        Args:
            request (HttpRequest): Django HTTP request object.

        Returns:
            Response: Rendered HTTP 200 response with Allow header.
        """
        response = Response(status=status.HTTP_200_OK)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {"request": request, "response": response}
        response = response.render()
        response["Allow"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    def _add_security_headers(self, request: HttpRequest, response: Response) -> Response:
        """Add comprehensive security headers to HTTP responses.

        Applies security headers including Content Security Policy (CSP),
        anti-clickjacking headers, and content type protection. CSP is
        applied based on request path patterns for granular control.

        Args:
            request (HttpRequest): Django HTTP request object.
            response (Response): Django HTTP response object to modify.

        Returns:
            Response: Response object with security headers applied.
        """
        origin = request.headers.get("Origin")
        allowed_origins = ["tauri://localhost", "http://localhost:3000"] if CONFIG.frontend_desktop else []
        for header, value in SECURITY_HEADERS.items():
            if header == "Content-Security-Policy":
                for path, csp in CSP.items():
                    if request.path.startswith(path):
                        value = csp
                        break
            elif header == "Access-Control-Allow-Origin":
                value = origin if origin in allowed_origins else CONFIG.frontend_url.replace(CONFIG.root_path, "")
            elif header == "Referrer-Policy" and request.path.startswith("/admin"):
                value = "strict-origin"  # pragma: no cover
            response[header] = value
        return response

    def _log_request_and_response(self, request: HttpRequest, response: Response):
        """Log HTTP request and response for security monitoring.

        Logs all HTTP transactions with appropriate log levels based on
        response status codes. Provides comprehensive audit trail for
        security monitoring and incident response.

        Log Levels:
            - INFO: Successful requests (2XX-3XX status codes)
            - WARNING: Client errors (4XX status codes)
            - ERROR: Server errors (5XX status codes)

        Args:
            request (HttpRequest): Django HTTP request object.
            response (Response): Django HTTP response object.
        """
        logger_level = self.logger.info
        if response.status_code >= 400 and response.status_code < 500:
            logger_level = self.logger.warning  # Warning level for 4XX error responses
        elif response.status_code >= 500:  # pragma: no cover
            logger_level = self.logger.error  # Error level for 5XX error responses
        logger_level(
            f"{request.method} {request.get_full_path()} > HTTP {response.status_code}",
            extra={"request": request, "response": response},
        )

    def __call__(self, request: HttpRequest) -> Any:
        """Process HTTP request through security middleware.

        Main middleware entry point that processes incoming HTTP requests
        by extracting client IP, handling CORS preflight requests,
        applying security headers, and logging all transactions.

        Processing Flow:
            1. Extract and normalize client IP address
            2. Store request in context-local storage for downstream components
            3. Handle OPTIONS requests
            4. Process request through Django middleware chain
            5. Apply comprehensive security headers
            6. Log request/response for security monitoring
            7. Clear request from context-local storage

        Args:
            request (HttpRequest): Incoming Django HTTP request.

        Returns:
            Any: Processed HTTP response with security controls applied.
        """
        request.META["REMOTE_ADDR"] = self._get_source_ip_address(request)
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

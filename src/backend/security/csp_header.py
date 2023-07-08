from typing import Any, Dict

# CSP for the API Rest
api = "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'"
# CSP for the Swagger-UI
swagger = (
    "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
    # 'unsafe-inline' required due to a inline script with hardcoded dynamic CSRF token, so its hash changes
    "script-src http://cdn.jsdelivr.net 'unsafe-inline'; "
    "style-src http://cdn.jsdelivr.net https://fonts.googleapis.com; "
    "img-src data: http://cdn.jsdelivr.net; "
    "connect-src 'self'; "
)
# CSP for Redoc
redoc = (
    "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
    "script-src http://cdn.jsdelivr.net; "
    "style-src http://cdn.jsdelivr.net https://fonts.googleapis.com "
    "'sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=' "
    "'sha256-m6OsjZ+ZE+8plS5r0wBVuIy/qbXuHEw//v/OhLyy9Xg='; "
    "img-src data: http://cdn.jsdelivr.net; "
    "font-src fonts.gstatic.com; "
    "worker-src blob:; "
    "child-src blob:; "
    "connect-src 'self'"
)
# CSP for Admin site
admin = (
    "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
    "script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'"
)


def add_csp_to_headers(headers: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
    '''Add CSP header to the response headers, based on endpoint accessed by the user.

    Args:
        headers (Dict[str, Any]): Current response headers
        endpoint (str): Endpoint accesed by the user

    Returns:
        Dict[str, Any]: Response headers including CSP
    '''
    headers['Content-Security-Policy'] = api
    if endpoint.startswith('/admin'):
        headers['Content-Security-Policy'] = admin
    elif endpoint.startswith('/api/schema/swagger-ui'):
        headers['Content-Security-Policy'] = swagger
    elif endpoint.startswith('/api/schema/redoc'):
        headers['Content-Security-Policy'] = redoc
    return headers

api = "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'"
swagger = (
    "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
    "script-src http://cdn.jsdelivr.net 'unsafe-inline'; "      # 'unsafe-inline' required due to a inline script with hardcoded dynamic CSRF token
    "style-src http://cdn.jsdelivr.net https://fonts.googleapis.com; "
    "img-src data: http://cdn.jsdelivr.net; "
    "connect-src 'self'; "
)
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
admin = (
    "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
    "script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'"
)


def get_headers_with_csp(headers: dict, path: str) -> dict:
    headers['Content-Security-Policy'] = api,
    if path.startswith('/admin'):
        headers['Content-Security-Policy'] = admin
    elif path.startswith('/api/schema/swagger-ui'):
        headers['Content-Security-Policy'] = swagger
    elif path.startswith('/api/schema/redoc'):
        headers['Content-Security-Policy'] = redoc
    return headers

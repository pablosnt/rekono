from typing import Any


class RekonoMiddleware:

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> Any:
        response = self.get_response(request)
        response['Server'] = None
        # response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' http://cdn.jsdelivr.net; style-src 'self' https://fonts.googleapis.com unsafe-inline; base-uri 'self'; object-src 'none'; frame-ancestors 'none'"
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Feature-Policy'] = "microphone 'none'; geolocation 'none'; gyroscope 'none'; camera 'none'; accelerometer 'none'"
        return response

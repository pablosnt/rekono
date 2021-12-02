from typing import Any

headers = {
    'Server': None,
    # 'Content-Security-Policy': (
    #     "default-src 'self'; script-src 'self' http://cdn.jsdelivr.net; "
    #     "style-src 'self' https://fonts.googleapis.com unsafe-inline; "
    #     "base-uri 'self'; object-src 'none'; frame-ancestors 'none'"
    # ),
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Feature-Policy': (
        "microphone 'none'; geolocation 'none'; "
        "gyroscope 'none'; camera 'none'; accelerometer 'none'"
    )
}


class RekonoMiddleware:

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> Any:
        response = self.get_response(request)
        for header, value in headers.items():
            response[header] = value
        return response

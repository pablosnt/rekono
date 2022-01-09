from typing import Any

from security.csp_header import get_headers_with_csp

headers = {
    'Server': None,
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'no-referrer'
}


class RekonoMiddleware:

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> Any:
        response = self.get_response(request)
        for header, value in get_headers_with_csp(headers, request.path).items():
            response[header] = value
        return response

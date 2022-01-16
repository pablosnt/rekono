from typing import Any

from security.csp_header import add_csp_to_headers

# Base response headers for all HTTP responses
headers = {
    'Server': None,
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'no-referrer'
}


class RekonoMiddleware:
    '''Security middleware that manages all HTTP requests and responses.'''

    def __init__(self, get_response: Any) -> None:
        '''Middleware constructor.

        Args:
            get_response (Any): HTTP request processor
        '''
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        '''Process HTTP requests when received and return HTTP responses.

        Args:
            request (Any): HTTP request

        Returns:
            Any: HTTP response
        '''
        response = self.get_response(request)                                   # Process request
        for header, value in add_csp_to_headers(headers, request.path).items():     # Get response headers with CSP
            response[header] = value                                            # Include response headers in response
        return response

import logging
from typing import Any

from rest_framework.request import HttpRequest
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

logger = logging.getLogger()                                                    # Rekono logger


class RekonoSecurityMiddleware:
    '''Security middleware that manages all HTTP requests and responses.'''

    def __init__(self, get_response: Any) -> None:
        '''Middleware constructor.

        Args:
            get_response (Any): HTTP request processor
        '''
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> Any:
        '''Process HTTP requests when received and return HTTP responses.

        Args:
            request (HttpRequest): HTTP request

        Returns:
            Any: HTTP response
        '''
        response = self.get_response(request)                                   # Process request
        for header, value in add_csp_to_headers(headers, request.path).items():     # Get response headers with CSP
            response[header] = value                                            # Include response headers in response
        log = logger.info                                                       # Info level by default
        if response.status_code >= 400 and response.status_code < 500:
            log = logger.warning                                                # Warning level for 4XX error responses
        elif response.status_code >= 500:
            log = logger.error                                                  # Error level for 5XX error responses
        log(f'{request.method} {request.get_full_path()} > HTTP {response.status_code}', extra={'request': request})
        return response

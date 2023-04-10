import logging
from typing import Any

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from security.csp_header import add_csp_to_headers

from rekono.settings import TRUSTED_PROXY

# Base response headers for all HTTP responses
headers = {
    'Server': None,
    'Cache-Control': 'no-store',
    'Referrer-Policy': 'no-referrer',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Access-Control-Allow-Origin': 'app://.',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'content-type, authorization',
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
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for and TRUSTED_PROXY:
            if ',' in x_forwarded_for:
                x_forwarded_for = x_forwarded_for.split(',', 1)[0]
            request.META['REMOTE_ADDR'] = x_forwarded_for
        if request.method == 'OPTIONS':                                         # Generic answer for OPTIONS requests
            response = Response(status=status.HTTP_200_OK)
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = 'application/json'
            response.renderer_context = {
                'request': request,
                'response': response
            }
            response = response.render()
            response['Allow'] = 'GET, POST, PUT, DELETE, OPTIONS'
        else:
            response = self.get_response(request)                               # Process request
        for header, value in add_csp_to_headers(headers, request.path).items():     # Get response headers with CSP
            response[header] = value                                            # Include response headers in response
        log = logger.info                                                       # Info level by default
        if response.status_code >= 400 and response.status_code < 500:
            log = logger.warning                                                # Warning level for 4XX error responses
        elif response.status_code >= 500:
            log = logger.error                                                  # Error level for 5XX error responses
        log(f'{request.method} {request.get_full_path()} > HTTP {response.status_code}', extra={'request': request})
        return response

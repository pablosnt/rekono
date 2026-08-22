"""Exception handling utilities for Django REST framework.

Provides a custom exception handler that converts database integrity
errors into user-friendly responses and delegates all other exceptions
to DRF's default handler.
"""

from typing import Any

from django.db.utils import IntegrityError
from psycopg.errors import UniqueViolation
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler


def handler(exc: Exception, context: dict[str, Any]) -> Response:
    """Handle the exceptions raised during the API requests.

    Database integrity violations are reported as a validation error, since they
    usually mean that the object already exists, and the rest of the exceptions are
    delegated to the default DRF handler. Both Django's wrapped IntegrityError and
    psycopg's UniqueViolation are checked defensively, so a unique constraint
    violation is caught whether it arrives wrapped (the normal case for all database
    access through Django) or as the underlying driver exception.

    Args:
        exc: Exception raised while the request was being processed.
        context: View, request, and arguments where the exception was raised, as
          provided by DRF.

    Returns:
        The response to send to the client, or None when the default DRF handler
        doesn't know the exception and it must be reported as a server error.
    """
    if exc.__class__ in [UniqueViolation, IntegrityError]:
        response = Response({"constraint": ["This object already exists"]}, status=HTTP_400_BAD_REQUEST)
    else:
        response = exception_handler(exc, context)
    return response

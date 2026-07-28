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
    """Custom exception handler for Django REST framework.

    Provides user-friendly error messages for database integrity violations
    and falls back to the default DRF exception handler for other exceptions.

    Args:
        exc (Exception): The exception that was raised.
        context (dict[str, Any]): Context information about the request.

    Returns:
        Response: HTTP response with appropriate error message and status code.

    Note:
        Both Django's wrapped IntegrityError and psycopg's UniqueViolation
        are checked defensively, so a unique constraint violation is caught
        whether it arrives wrapped (the normal case for all database access
        through Django) or as the underlying driver exception.
    """
    if exc.__class__ in [UniqueViolation, IntegrityError]:
        response = Response({"constraint": ["This object already exists"]}, status=HTTP_400_BAD_REQUEST)
    else:
        response = exception_handler(exc, context)
    return response

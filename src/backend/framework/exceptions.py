"""This module defines custom exception classes."""

from typing import Any

from django.db.utils import IntegrityError
from psycopg.errors import UniqueViolation
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler


def handler(exc: Exception, context: dict[str, Any]) -> Response:
    """Handle exceptions for the REST framework.

    This handler provides custom error responses for specific exception types,
    particularly database integrity errors and unique constraint violations.

    Args:
        exc: The exception that was raised.
        context: Context dictionary containing request and view information.

    Returns:
        Custom Response object with appropriate error details.
    """
    if exc.__class__ in [UniqueViolation, IntegrityError]:
        response = Response({"constraint": ["This object already exists"]}, status=HTTP_400_BAD_REQUEST)
    else:
        response = exception_handler(exc, context)
    return response

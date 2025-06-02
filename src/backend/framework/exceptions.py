from django.db.utils import IntegrityError
from psycopg.errors import UniqueViolation
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler


def exceptions_handler(exc, context):
    if exc.__class__ in [UniqueViolation, IntegrityError]:
        response = Response(
            {"constraint": ["This object already exists"]},
            status=HTTP_400_BAD_REQUEST,
        )
    else:
        response = exception_handler(exc, context)
    return response

"""This module provides pagination utilities."""

from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Custom pagination configuration for API responses.

    This class provides standardized pagination settings for the API,
    including page size limits and query parameter names.

    Attributes:
        page_query_param (str): Query parameter name for page number.
        page_size_query_param (str): Query parameter name for page size.
        page_size (int): Default number of items per page.
        max_page_size (int): Maximum number of items per page.
    """

    page_query_param = "page"
    page_size_query_param = "limit"
    page_size = 25
    max_page_size = 1000

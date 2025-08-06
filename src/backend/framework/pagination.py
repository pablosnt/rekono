
"""Pagination configuration for Django REST framework API endpoints.

Provides standardized pagination settings for consistent API responses
across all Rekono endpoints.
"""

from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Standard pagination configuration for Rekono API endpoints.

    Provides consistent pagination behavior across all API endpoints
    with configurable page sizes and reasonable defaults.

    Attributes:
        page_query_param (str): Query parameter name for page number.
        page_size_query_param (str): Query parameter name for page size.
        page_size (int): Default number of items per page.
        max_page_size (int): Maximum allowed items per page.

    Example:
        API Usage:
        - GET /api/items/?page=2&limit=50
        - Returns page 2 with 50 items per page (if within max limit)
    """

    page_query_param = "page"
    page_size_query_param = "limit"
    page_size = 25
    max_page_size = 1000

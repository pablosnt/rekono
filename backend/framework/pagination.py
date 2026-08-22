"""Pagination applied by default to all the Rekono API endpoints."""

from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Page number pagination shared by all the Rekono API endpoints.

    Attributes:
        page_query_param: Query parameter that selects the requested page.
        page_size_query_param: Query parameter that overrides the page size.
        page_size: Number of items returned when the client doesn't ask for a size.
        max_page_size: Upper bound for the requested page size.
    """

    page_query_param = "page"
    page_size_query_param = "limit"
    page_size = 25
    max_page_size = 1000

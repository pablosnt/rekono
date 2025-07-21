from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "limit"
    page_size = 25
    max_page_size = 1000

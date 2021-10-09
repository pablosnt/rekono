from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'size'
    page_size = 100
    max_page_size = 1000

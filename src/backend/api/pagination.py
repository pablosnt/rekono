from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    '''Pagination configuration for API Rest.'''

    page_query_param = 'page'                                                   # Page parameter
    page_size_query_param = 'limit'                                             # Size parameter
    page_size = 25                                                              # Default page size
    max_page_size = 1000                                                        # Max page size

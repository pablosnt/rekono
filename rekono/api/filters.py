from typing import Any, List

from django.db.models import Q, QuerySet
from django.views import View
from django_filters.rest_framework import (DjangoFilterBackend, FilterSet,
                                           filters)
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from tools.models import Tool


class RekonoFilterBackend(DjangoFilterBackend):
    '''Rekono filter backend from DjangoFilterBackend.

    This can't be added as default backend because cause warnings when access swagger-ui.
    This is required at least for Finding views to allow filters by N-M relations like 'executions' field.
    '''

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> Any:
        '''Filter queryset.

        Args:
            request (Request): HTTP request
            queryset (QuerySet): Queryset to filter
            view (View): Django view affected

        Returns:
            Any: Filtered queryset
        '''
        return super().filter_queryset(request, queryset, view).distinct()


class RekonoSearchFilter(SearchFilter):
    '''Rekono search filter from SearchFilter.'''

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        '''Filter queryset.

        Args:
            request (Request): HTTP request
            queryset (QuerySet): Queryset to filter
            view (View): Django view affected

        Returns:
            QuerySet: Filtered queryset
        '''
        return super().filter_queryset(request, queryset, view).distinct()      # Ignore duplicates if exist


class RekonoOrderingFilter(OrderingFilter):
    '''Rekono ordering filter from OrderingFilter.'''

    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        '''Filter queryset.

        Args:
            request (Request): HTTP request
            queryset (QuerySet): Queryset to filter
            view (View): Django view affected

        Returns:
            QuerySet: Filtered queryset
        '''
        return super().filter_queryset(request, queryset, view).distinct()      # Ignore duplicates if exist


class RekonoMultipleFieldFilter(FilterSet):
    '''Filter that allows querysets filtering using two model fields.'''

    def multiple_field_filter(self, queryset: QuerySet, value: Any, fields: List[str]) -> QuerySet:
        '''Filter queryset using two model fields simultaneously.

        Args:
            queryset (QuerySet): Queryset to be filtered
            value (Any): Value to filter the queryset
            fields (List[str]): List with the name of the fields to use

        Returns:
            QuerySet: Queryset filtered by the two fields
        '''
        filter_query = Q()
        for field in fields:
            filter_query |= Q(**{field: value})
        return queryset.filter(filter_query)


class BaseToolFilter(RekonoMultipleFieldFilter):
    '''Filter that allows querysets filtering by Tool using two model fields.'''

    tool = filters.NumberFilter(field_name='tool', method='filter_tool')        # Tool Id given by the user
    tool_fields: List[str] = []                                                 # Tool field names to use in the filter

    def filter_tool(self, queryset: QuerySet, name: str, value: Tool) -> QuerySet:
        '''Filter queryset by Tool using two model fields simultaneously.

        Args:
            queryset (QuerySet): Queryset to be filtered
            name (str): Field name. Not used in this case
            value (Tool): Tool to filter the queryset

        Returns:
            QuerySet: Queryset filtered by the Tool using the defined 'tool_fields'
        '''
        return self.multiple_field_filter(queryset, value, self.tool_fields)

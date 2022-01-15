from typing import Any

from django.db.models import Q, QuerySet
from django_filters.rest_framework import FilterSet, filters
from tools.models import Tool


class BaseFilter(FilterSet):
    '''Filter that allows querysets filtering using two model fields.'''

    def multiple_field_filter(self, queryset: QuerySet, value: Any, fields: tuple) -> QuerySet:
        '''Filter queryset using two model fields simultaneously.

        Args:
            queryset (QuerySet): Queryset to be filtered
            value (Any): Value to filter the queryset
            fields (tuple): Tuple with the name of the two fields to use

        Returns:
            QuerySet: Queryset filtered by the two fields
        '''
        field1, field2 = fields
        filter1: dict = {field1: value}
        filter2: dict = {field2: value}
        return queryset.filter(Q(**filter1) | Q(**filter2))


class ToolFilter(BaseFilter):
    '''Filter that allows querysets filtering by Tool using two model fields.'''

    tool = filters.NumberFilter(field_name='tool', method='filter_tool')        # Tool Id given by the user
    tool_fields: tuple = ()                                                     # Tool field names to use in the filter

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

from django.db.models import Q
from django_filters import rest_framework
from django_filters.rest_framework import filters


class ToolFilter(rest_framework.FilterSet):
    tool = filters.NumberFilter(field_name='tool', method='filter_tool')
    tool_fields = ()

    def filter_tool(self, queryset, name, value):
        field1, field2 = self.tool_fields
        filter1 = {field1: value}
        filter2 = {field2: value}
        return queryset.filter(Q(**filter1) | Q(**filter2))

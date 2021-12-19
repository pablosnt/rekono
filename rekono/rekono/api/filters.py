from typing import Tuple

from django.db.models import Q
from django_filters import rest_framework
from django_filters.rest_framework import filters


class BaseFilter(rest_framework.FilterSet):

    def related_field_filter(self, queryset, name, value):
        filter = {name: value}
        return queryset.filter(**filter).all().distinct()

    def multiple_field_filter(self, queryset, value, fields):
        field1, field2 = fields
        filter1 = {field1: value}
        filter2 = {field2: value}
        return queryset.filter(Q(**filter1) | Q(**filter2))


class ToolFilter(BaseFilter):
    tool = filters.NumberFilter(field_name='tool', method='filter_tool')
    tool_fields: Tuple[str, str] = ()

    def filter_tool(self, queryset, name, value):
        return self.multiple_field_filter(queryset, value, self.tool_fields)

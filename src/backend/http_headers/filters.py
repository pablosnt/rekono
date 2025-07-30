"""Django REST framework filters for HTTP header models.

This module provides filtering capabilities for HTTP header records,
allowing users to filter HTTP header data by various criteria such
as project, target, user, key, and value.
"""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from http_headers.models import HttpHeader
from projects.models import Project


class HttpHeaderFilter(FilterSet):
    """Filter set for HttpHeader model.

    This class provides filtering capabilities for HTTP header records,
    allowing filtering by project, target, user, key, and value.

    Attributes:
        project (ModelChoiceFilter): Filter by project associated with the
            HTTP header record.
    """

    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="target__project")

    class Meta:
        model = HttpHeader
        fields = {
            "target": ["exact", "isnull"],
            "user": ["exact", "isnull"],
            "key": ["exact", "icontains"],
            "value": ["exact", "icontains"],
        }

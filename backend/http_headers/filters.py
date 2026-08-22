"""Filters of the HTTP header endpoints."""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from http_headers.models import HttpHeader
from projects.models import Project


class HttpHeaderFilter(FilterSet):
    """Filters to search the HTTP headers that the tools send.

    Attributes:
        project: Filter by the project of the target that the header belongs to.
    """

    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="target__project", help_text="Filter headers by associated project"
    )

    class Meta:
        """Filter configuration for the HTTP headers."""

        model = HttpHeader
        fields = {
            "target": ["exact", "isnull"],
            "user": ["exact", "isnull"],
            "key": ["exact", "icontains"],
            "value": ["exact", "icontains"],
        }

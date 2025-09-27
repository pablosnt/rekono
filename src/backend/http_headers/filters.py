"""HTTP Headers filters for advanced API querying.

Provides filtering capabilities for HTTP headers with support for
project-based filtering and field-specific search operations.
"""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from http_headers.models import HttpHeader
from projects.models import Project


class HttpHeaderFilter(FilterSet):
    """FilterSet for HTTP header querying and filtering.

    Provides comprehensive filtering capabilities for HTTP headers
    including project-based filtering, exact matches, and text searches
    to enable efficient header management and discovery.

    Attributes:
        project (ModelChoiceFilter): Filter headers by associated project
    """

    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="target__project", help_text="Filter headers by associated project"
    )

    class Meta:
        """Meta configuration for HttpHeaderFilter.

        Defines the model and available filter fields with their
        supported lookup types for comprehensive header querying.

        Attributes:
            model (type): HttpHeader model class
            fields (dict): Field names mapped to supported lookups
        """

        model = HttpHeader
        fields = {
            "target": ["exact", "isnull"],
            "user": ["exact", "isnull"],
            "key": ["exact", "icontains"],
            "value": ["exact", "icontains"],
        }

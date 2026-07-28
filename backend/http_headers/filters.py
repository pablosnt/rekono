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

    Provides filtering and search operations for HTTP headers based on
    associated project, target, user, key, and value.

    Attributes:
        project (ModelChoiceFilter): Filter headers by associated project, through the target relationship
    """

    project = ModelChoiceFilter(
        queryset=Project.objects.all(), field_name="target__project", help_text="Filter headers by associated project"
    )

    class Meta:
        """Meta configuration for HttpHeaderFilter.

        Attributes:
            model (Model): The HttpHeader model to filter
            fields (dict): Field names mapped to supported lookup types
        """

        model = HttpHeader
        fields = {
            "target": ["exact", "isnull"],
            "user": ["exact", "isnull"],
            "key": ["exact", "icontains"],
            "value": ["exact", "icontains"],
        }

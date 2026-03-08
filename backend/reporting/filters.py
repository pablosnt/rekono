"""Django filter classes for security report querying and filtering.

Provides filtering capabilities for report queries through REST API endpoints
with support for exact matches and date range filtering.
"""

from django_filters.rest_framework import CharFilter, FilterSet

from reporting.models import Report


class ReportFilter(FilterSet):
    """Filter class for Report model queries.

    Provides filtering capabilities for report queries including exact matches
    on key fields and date range filtering for report creation timestamps.
    """

    report_format = CharFilter(field_name="format", lookup_expr="exact")

    class Meta:
        """Meta configuration for the ReportFilter.

        Attributes:
            model (Model): The Report model to filter.
            fields (dict): Field names mapped to allowed filter operations.
        """

        model = Report
        fields = {
            "project": ["exact"],
            "target": ["exact"],
            "task": ["exact"],
            "status": ["exact"],
            "user": ["exact"],
            "date": ["gte", "lte", "exact"],
        }

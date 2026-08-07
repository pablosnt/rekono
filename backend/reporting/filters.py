"""Filters of the report endpoints."""

from django_filters.rest_framework import CharFilter, FilterSet

from reporting.models import Report


class ReportFilter(FilterSet):
    """Filters to search the reports of a project.

    Attributes:
        report_format: Filter by the format of the report. It isn't called format
          because that's the query parameter that DRF uses to select the renderer.
    """

    report_format = CharFilter(field_name="format", lookup_expr="exact")

    class Meta:
        """Filter configuration for the reports."""

        model = Report
        fields = {
            "project": ["exact"],
            "target": ["exact"],
            "task": ["exact"],
            "status": ["exact"],
            "user": ["exact"],
            "date": ["gte", "lte", "exact"],
        }

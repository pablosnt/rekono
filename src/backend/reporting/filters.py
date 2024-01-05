from django_filters.rest_framework import FilterSet
from reporting.models import Report


class ReportFilter(FilterSet):
    class Meta:
        model = Report
        fields = {
            "project": ["exact"],
            "target": ["exact"],
            "task": ["exact"],
            "status": ["exact"],
            "format": ["exact"],
            "user": ["exact"],
            "date": ["gte", "lte", "exact"],
        }

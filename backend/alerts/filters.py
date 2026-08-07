"""Filters of the alert endpoints."""

from django_filters.rest_framework import FilterSet

from alerts.models import Alert


class AlertFilter(FilterSet):
    """Filters to search the alerts of a project."""

    class Meta:
        """Filter configuration for the alerts."""

        model = Alert
        fields = {
            "project": ["exact"],
            "item": ["exact"],
            "value": ["exact", "icontains"],
            "enabled": ["exact"],
            "owner": ["exact"],
            "subscribers": ["exact"],
        }

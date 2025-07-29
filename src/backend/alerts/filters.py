"""Django filters for alert management.

This module contains the filter classes used for querying and filtering
alert objects in the REST API.
"""

from django_filters.rest_framework import FilterSet

from alerts.models import Alert


class AlertFilter(FilterSet):
    """Filter class for Alert model.

    Provides filtering capabilities for alert queries based on various
    fields including project, item type, mode, value, enabled status,
    owner, and subscribers.
    """

    class Meta:
        model = Alert
        fields = {
            "project": ["exact"],
            "item": ["exact"],
            "mode": ["exact"],
            "value": ["exact", "icontains"],
            "enabled": ["exact"],
            "owner": ["exact"],
            "subscribers": ["exact"],
        }

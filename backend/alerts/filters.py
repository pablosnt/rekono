"""Django filters for alert management.

Filter classes for querying and filtering alert objects in the REST API.
Provides field-based filtering capabilities for alert searches.
"""

from django_filters.rest_framework import FilterSet

from alerts.models import Alert


class AlertFilter(FilterSet):
    """Filter class for Alert model.

    Provides filtering capabilities for alert queries based on project,
    item type, value, enabled status, owner, and subscribers.
    """

    class Meta:
        """Meta configuration for the AlertFilter.

        Attributes:
            model (Model): The Alert model to filter
            fields (dict): Field names and their supported filter operations
        """

        model = Alert
        fields = {
            "project": ["exact"],
            "item": ["exact"],
            "value": ["exact", "icontains"],
            "enabled": ["exact"],
            "owner": ["exact"],
            "subscribers": ["exact"],
        }

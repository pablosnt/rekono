from django_filters.rest_framework import FilterSet

from alerts.models import Alert


class AlertFilter(FilterSet):
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

from alerts.models import Alert
from django_filters.rest_framework import FilterSet


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

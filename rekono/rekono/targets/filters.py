from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from targets.models import Target


class TargetFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('project', 'target', 'type'))

    class Meta:
        model = Target
        fields = {
            'project__name': ['exact', 'contains'],
            'project__description': ['exact', 'contains'],
            'project__owner': ['exact'],
            'target': ['exact', 'contains'],
            'type': ['exact'],
        }

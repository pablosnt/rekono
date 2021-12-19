from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from targets.models import Target


class TargetFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('project', 'target', 'type'))

    class Meta:
        model = Target
        fields = {
            'project__name': ['exact', 'iexact', 'contains', 'icontains'],
            'project__description': ['exact', 'iexact', 'contains', 'icontains'],
            'project__owner': ['exact'],
            'project__owner__username': ['exact', 'iexact', 'contains', 'icontains'],
            'target': ['exact', 'iexact', 'contains', 'icontains'],
            'type': ['exact'],
        }

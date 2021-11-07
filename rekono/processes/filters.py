from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from processes.models import Process, Step


class ProcessFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('name', 'creator'))

    class Meta:
        model = Process
        fields = {
            'name': ['exact', 'contains'],
            'description': ['exact', 'contains'],
            'creator': ['exact'],
        }


class StepFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('process', 'tool', 'configuration', 'priority'))

    class Meta:
        model = Step
        fields = {
            'process__name': ['exact', 'contains'],
            'process__description': ['exact', 'contains'],
            'process__creator': ['exact'],
            'tool': ['exact'],
            'configuration': ['exact'],
            'priority': ['exact'],
        }

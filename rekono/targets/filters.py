from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from targets.models import Target, TargetEndpoint, TargetPort


class TargetFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('project', 'target', 'type'))

    class Meta:
        model = Target
        fields = {
            'project': ['exact'],
            'project__name': ['exact', 'iexact', 'contains', 'icontains'],
            'project__description': ['exact', 'iexact', 'contains', 'icontains'],
            'project__owner': ['exact'],
            'project__owner__username': ['exact', 'iexact', 'contains', 'icontains'],
            'target': ['exact', 'iexact', 'contains', 'icontains'],
            'type': ['exact'],
        }


class TargetPortFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('target', 'port'))

    class Meta:
        model = TargetPort
        fields = {
            'target': ['exact'],
            'target__project': ['exact'],
            'target__project__name': ['exact', 'iexact', 'contains', 'icontains'],
            'target__project__description': ['exact', 'iexact', 'contains', 'icontains'],
            'target__project__owner': ['exact'],
            'target__project__owner__username': ['exact', 'iexact', 'contains', 'icontains'],
            'target__target': ['exact', 'iexact', 'contains', 'icontains'],
            'target__type': ['exact'],
            'port': ['exact']
        }


class TargetEndpointFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('target_port', 'endpoint'))

    class Meta:
        model = TargetEndpoint
        fields = {
            'target_port': ['exact'],
            'target_port__port': ['exact'],
            'target_port__target': ['exact'],
            'target_port__target__project': ['exact'],
            'target_port__target__project__name': ['exact', 'iexact', 'contains', 'icontains'],
            'target_port__target__project__description': ['exact', 'iexact', 'contains', 'icontains'],
            'target_port__target__project__owner': ['exact'],
            'target_port__target__project__owner__username': ['exact', 'iexact', 'contains', 'icontains'],
            'target_port__target__target': ['exact', 'iexact', 'contains', 'icontains'],
            'target_port__target__type': ['exact'],
            'endpoint': ['exact', 'iexact', 'contains', 'icontains']
        }

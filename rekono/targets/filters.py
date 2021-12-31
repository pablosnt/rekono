from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from targets.models import Target, TargetEndpoint, TargetPort


class TargetFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('project', 'target', 'type'))

    class Meta:
        model = Target
        fields = {
            'project': ['exact'],
            'project__name': ['exact', 'icontains'],
            'project__owner': ['exact'],
            'project__owner__username': ['exact', 'icontains'],
            'target': ['exact', 'icontains'],
            'target_ports__port': ['exact'],
            'target_ports__target_endpoints__endpoint': ['exact', 'icontains'],
            'type': ['exact'],
        }


class TargetPortFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('target', 'port'))

    class Meta:
        model = TargetPort
        fields = {
            'target': ['exact'],
            'target__project': ['exact'],
            'target__project__name': ['exact', 'icontains'],
            'target__project__owner': ['exact'],
            'target__project__owner__username': ['exact', 'icontains'],
            'target__target': ['exact', 'icontains'],
            'target_endpoints__endpoint': ['exact', 'icontains'],
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
            'target_port__target__project__name': ['exact', 'icontains'],
            'target_port__target__project__owner': ['exact'],
            'target_port__target__project__owner__username': ['exact', 'icontains'],
            'target_port__target__target': ['exact', 'icontains'],
            'target_port__target__type': ['exact'],
            'endpoint': ['exact', 'icontains']
        }

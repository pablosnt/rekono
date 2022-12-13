from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter

from targets.models import (Target, TargetPort, TargetTechnology,
                            TargetVulnerability)


class TargetFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort Target entities.'''

    o = OrderingFilter(fields=('project', 'target', 'type'))                    # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = Target
        fields = {                                                              # Filter fields
            'project': ['exact'],
            'project__name': ['exact', 'icontains'],
            'project__owner': ['exact'],
            'project__owner__username': ['exact', 'icontains'],
            'target': ['exact', 'icontains'],
            'type': ['exact'],
        }


class TargetPortFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort Target Port entities.'''

    o = OrderingFilter(fields=('target', 'port'))                               # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = TargetPort
        fields = {                                                              # Filter fields
            'target': ['exact'],
            'target__project': ['exact'],
            'target__project__name': ['exact', 'icontains'],
            'target__project__owner': ['exact'],
            'target__project__owner__username': ['exact', 'icontains'],
            'target__target': ['exact', 'icontains'],
            'target__type': ['exact'],
            'port': ['exact']
        }


class TargetTechnologyFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort Target Technology entities.'''

    o = OrderingFilter(fields=('target_port', 'name'))                          # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = TargetTechnology
        fields = {                                                              # Filter fields
            'target_port': ['exact'],
            'target_port__port': ['exact'],
            'target_port__target': ['exact'],
            'target_port__target__project': ['exact'],
            'target_port__target__project__name': ['exact', 'icontains'],
            'target_port__target__project__owner': ['exact'],
            'target_port__target__project__owner__username': ['exact', 'icontains'],
            'target_port__target__target': ['exact', 'icontains'],
            'target_port__target__type': ['exact'],
            'name': ['exact', 'icontains'],
            'version': ['exact', 'icontains'],
        }


class TargetVulnerabilityFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort Target Vulnerability entities.'''

    o = OrderingFilter(fields=('target_port', 'cve'))                           # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = TargetVulnerability
        fields = {                                                              # Filter fields
            'target_port': ['exact'],
            'target_port__port': ['exact'],
            'target_port__target': ['exact'],
            'target_port__target__project': ['exact'],
            'target_port__target__project__name': ['exact', 'icontains'],
            'target_port__target__project__owner': ['exact'],
            'target_port__target__project__owner__username': ['exact', 'icontains'],
            'target_port__target__target': ['exact', 'icontains'],
            'target_port__target__type': ['exact'],
            'cve': ['exact']
        }

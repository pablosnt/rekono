from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter

from parameters.models import InputTechnology, InputVulnerability


class InputTechnologyFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort input Technology entities.'''

    o = OrderingFilter(fields=('target_port', 'name'))                          # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = InputTechnology
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


class InputVulnerabilityFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort input Vulnerability entities.'''

    o = OrderingFilter(fields=('target_port', 'cve'))                           # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = InputVulnerability
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

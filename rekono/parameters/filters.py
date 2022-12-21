from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter

from parameters.models import InputTechnology, InputVulnerability


class InputTechnologyFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort input Technology entities.'''

    o = OrderingFilter(fields=('target', 'name'))                               # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = InputTechnology
        fields = {                                                              # Filter fields
            'target': ['exact'],
            'target__target': ['exact'],
            'name': ['exact', 'icontains'],
            'version': ['exact', 'icontains'],
        }


class InputVulnerabilityFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort input Vulnerability entities.'''

    o = OrderingFilter(fields=('target', 'cve'))                                # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = InputVulnerability
        fields = {                                                              # Filter fields
            'target': ['exact'],
            'target__target': ['exact'],
            'cve': ['exact']
        }

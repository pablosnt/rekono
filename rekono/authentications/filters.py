from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter

from authentications.models import Authentication


class AuthenticationFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort authentications entities.'''

    o = OrderingFilter(fields=('target_port', 'name', 'type'))                  # Ordering fields

    class Meta:
        model = Authentication
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
            'type': ['exact']
        }

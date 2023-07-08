from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from projects.models import Project


class ProjectFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort Project entities.'''

    o = OrderingFilter(fields=('name', 'owner'))                                # Ordering fields

    class Meta:
        '''FilterSet metadata.'''

        model = Project
        fields = {                                                              # Filter fields
            'name': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
            'owner': ['exact'],
            'owner__username': ['exact', 'icontains'],
            'members': ['exact'],
            'tags__name': ['in'],
        }

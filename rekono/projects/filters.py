from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from projects.models import Project


class ProjectFilter(rest_framework.FilterSet):
    o = OrderingFilter(fields=('name', 'owner'))

    class Meta:
        model = Project
        fields = {
            'name': ['exact', 'iexact', 'contains', 'icontains'],
            'description': ['exact', 'iexact', 'contains', 'icontains'],
            'owner': ['exact'],
            'owner__username': ['exact', 'iexact', 'contains', 'icontains'],
            'members': ['exact'],
        }

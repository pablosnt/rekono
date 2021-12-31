from django.db.models import Q, query
from django_filters import rest_framework
from django_filters.rest_framework import filters
from django_filters.rest_framework.filters import OrderingFilter
from projects.models import Project
from users.models import User


class UserFilter(rest_framework.FilterSet):
    o = OrderingFilter(
        fields=('username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined'),
    )
    project = filters.NumberFilter(field_name='project', method='filter_project_members')
    project__ne = filters.NumberFilter(field_name='project__ne', method='filter_project_members_ne')

    class Meta:
        model = User
        fields = {
            'username': ['exact', 'iexact', 'contains', 'icontains'],
            'first_name': ['exact', 'iexact', 'contains', 'icontains'],
            'last_name': ['exact', 'iexact', 'contains', 'icontains'],
            'email': ['exact', 'iexact', 'contains', 'icontains'],
            'is_active': ['exact'],
            'date_joined': ['gte', 'lte', 'exact'],
            'groups': ['exact'],
        }
    
    def filter_project_members(self, queryset, name, value):
        try:
            # TODO: Unauthorized access to project members access
            project = Project.objects.get(pk=value)
            return project.members.all()
        except Project.DoesNotExist:
            return queryset.none()

    def filter_project_members_ne(self, queryset, name, value):
        try:
            # TODO: Unauthorized access to no project members access
            project = Project.objects.get(pk=value)
            return queryset.filter(is_active=True).exclude(
                id__in=project.members.all().values('id')
            )
        except Project.DoesNotExist:
            return queryset.all()


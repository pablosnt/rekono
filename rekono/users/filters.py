from django.db.models import QuerySet
from django_filters import rest_framework
from django_filters.rest_framework import filters
from django_filters.rest_framework.filters import OrderingFilter
from projects.models import Project
from security.authorization.roles import Role
from users.models import User


class UserFilter(rest_framework.FilterSet):
    '''FilterSet to filter and sort User entities.'''

    # Ordering fields
    o = OrderingFilter(fields=('username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined'))
    role = filters.ChoiceFilter(field_name='role', method='filter_role', choices=Role.choices)  # Filter by user role
    # Get users that are members of these project
    project = filters.NumberFilter(field_name='project', method='filter_project_members')
    # Get users that aren't members of these project
    project__ne = filters.NumberFilter(field_name='project__ne', method='filter_project_members_ne')

    class Meta:
        '''FilterSet metadata.'''

        model = User
        fields = {                                                              # Filtering fields
            'username': ['exact', 'icontains'],
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'is_active': ['exact'],
            'date_joined': ['gte', 'lte', 'exact'],
            'groups': ['exact'],
        }

    def filter_role(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        '''Filter queryset by user role.

        Args:
            queryset (QuerySet): User queryset to be filtered
            name (str): Field name, not used in this case
            value (int): User role

        Returns:
            QuerySet: Filtered queryset by user role
        '''
        return queryset.filter(groups__name=value).all()

    def filter_project_members(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        '''Filter queryset, including only users that are members of a specific project.

        Args:
            queryset (QuerySet): User queryset to be filtered
            name (str): Field name, not used in this case
            value (int): Project Id

        Returns:
            QuerySet: Filtered queryset by project
        '''
        try:
            project = Project.objects.get(pk=value, members=self.request.user)
            return project.members.all().order_by('-id')
        except Project.DoesNotExist:
            return queryset.none()

    def filter_project_members_ne(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        '''Filter queryset, including only users that aren't members of a specific project.

        Args:
            queryset (QuerySet): User queryset to be filtered
            name (str): Field name, not used in this case
            value (int): Project Id

        Returns:
            QuerySet: Filtered queryset by project
        '''
        try:
            project = Project.objects.get(pk=value, members=self.request.user)
            return queryset.filter(is_active=True).exclude(id__in=project.members.all().values('id'))
        except Project.DoesNotExist:
            return queryset.all()

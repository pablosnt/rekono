from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter
from users.models import User


class UserFilter(rest_framework.FilterSet):
    o = OrderingFilter(
        fields=('username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined'),
    )

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

from django_filters import rest_framework
from django_filters.rest_framework.filters import OrderingFilter

from settings.models import Setting


class SettingFilter(rest_framework.FilterSet):

    o = OrderingFilter(fields=('field', 'private'))

    class Meta:
        model = Setting
        fields = {
            'field': ['exact', 'icontains'],
            'private': ['exact']
        }

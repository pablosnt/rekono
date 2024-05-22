from django_filters.rest_framework import FilterSet
from target_denylist.models import TargetDenylist


class TargetDenylistFilter(FilterSet):
    class Meta:
        model = TargetDenylist
        fields = {"target": ["exact", "icontains"], "default": ["exact"]}

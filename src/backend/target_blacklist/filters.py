from django_filters.rest_framework import FilterSet
from target_blacklist.models import TargetBlacklist


class TargetBlacklistFilter(FilterSet):
    class Meta:
        model = TargetBlacklist
        fields = {"target": ["exact", "icontains"], "default": ["exact"]}

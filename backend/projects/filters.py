"""Filters of the project endpoints."""

from django_filters.filters import CharFilter, ModelChoiceFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from projects.models import Project
from targets.models import Target


class ProjectFilter(FilterSet):
    """Filters to search projects by their data and their DefectDojo synchronization.

    Attributes:
        tag: Filter by one of the tags of the project.
        defectdojo_product: Filter by the DefectDojo product that the project is
          synchronized with.
        defectdojo_engagement: Filter by the DefectDojo engagement that the project
          is synchronized with.
        owner_username: Filter by the username of the owner.
        target: Filter by one of the targets of the project.
    """

    tag = CharFilter(field_name="tags__name")
    defectdojo_product = NumberFilter(field_name="defectdojo_sync__product_id")
    defectdojo_engagement = NumberFilter(field_name="defectdojo_sync__engagement_id")
    owner_username = CharFilter(field_name="owner__username", lookup_expr="icontains")
    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="targets")

    class Meta:
        """Filter configuration for the projects."""

        model = Project
        fields = {
            "name": ["exact", "icontains"],
            "owner": ["exact"],
            "members": ["exact"],
            "defectdojo_sync": ["exact"],
        }

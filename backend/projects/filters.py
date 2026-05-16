"""Django filters for project model queries.

Provides filter classes for advanced project querying with support for
tag-based filtering and DefectDojo integration parameters.
"""

from django_filters.filters import CharFilter, ModelChoiceFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from projects.models import Project
from targets.models import Target


# TODO: Fix filters defining custom filters instead of Attributes in the docstrings!
class ProjectFilter(FilterSet):
    """Filter class for Project model queries.

    Provides advanced filtering capabilities for project queries including
    tag-based filtering and DefectDojo integration parameters for enhanced
    project search and organization features.

    Custom Filters:
        tag: Filter projects by tag names
        defectdojo_product: Filter by DefectDojo product ID
        defectdojo_engagement: Filter by DefectDojo engagement ID
        owner_username: Filter by owner username
    """

    tag = CharFilter(field_name="tags__name")
    defectdojo_product = NumberFilter(field_name="defectdojo_sync__product_id")
    defectdojo_engagement = NumberFilter(field_name="defectdojo_sync__engagement_id")
    owner_username = CharFilter(field_name="owner__username", lookup_expr="icontains")
    target = ModelChoiceFilter(queryset=Target.objects.all(), field_name="targets")

    class Meta:
        """Meta configuration for the ProjectFilter.

        Defines the model and available filter fields for project queries
        including exact matches and case-insensitive text searches.

        Attributes:
            model (Model): The Project model to filter
            fields (dict): Available filter operations for each field
        """

        model = Project
        fields = {
            "name": ["exact", "icontains"],
            "owner": ["exact"],
            "members": ["exact"],
            "defectdojo_sync": ["exact"],
        }

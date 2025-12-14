"""Django filters for project model queries.

Provides filter classes for advanced project querying with support for
tag-based filtering and DefectDojo integration parameters.
"""

from django_filters.filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from projects.models import Project


class ProjectFilter(FilterSet):
    """Filter class for Project model queries.

    Provides advanced filtering capabilities for project queries including
    tag-based filtering and DefectDojo integration parameters for enhanced
    project search and organization features.

    Custom Filters:
        tag: Filter projects by tag names
        defectdojo_product_type: Filter by DefectDojo product type ID
        defectdojo_product: Filter by DefectDojo product ID
        defectdojo_engagement: Filter by DefectDojo engagement ID
    """

    tag = CharFilter(field_name="tags__name")
    owner = CharFilter(field_name="owner__username")
    defectdojo_product_type = NumberFilter(field_name="defectdojo_sync__product_type_id")
    defectdojo_product = NumberFilter(field_name="defectdojo_sync__product_id")
    defectdojo_engagement = NumberFilter(field_name="defectdojo_sync__engagement_id")

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
            "owner_id": ["exact"],
            "members": ["exact"],
            "defectdojo_sync": ["exact"],
        }

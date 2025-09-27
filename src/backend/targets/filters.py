"""Django filters for target management.

Filter classes for querying and filtering target objects in the REST API.
Provides field-based filtering capabilities for target searches including
DefectDojo integration filters.
"""

from django_filters.filters import NumberFilter
from django_filters.rest_framework import FilterSet

from targets.models import Target


class TargetFilter(FilterSet):
    """Filter class for Target model.

    Provides filtering capabilities for target queries based on project,
    target specification, type, and DefectDojo synchronization status
    with specialized filters for DefectDojo integration fields.

    Attributes:
        defectdojo_product_type (NumberFilter): Filter by DefectDojo product type ID
        defectdojo_product (NumberFilter): Filter by DefectDojo product ID
        defectdojo_engagement (NumberFilter): Filter by DefectDojo engagement ID
    """

    defectdojo_product_type = NumberFilter(field_name="defectdojo_sync__defectdojo_sync__product_type_id")
    defectdojo_product = NumberFilter(field_name="defectdojo_sync__defectdojo_sync__product_id")
    defectdojo_engagement = NumberFilter(field_name="defectdojo_sync__engagement_id")

    class Meta:
        """Meta configuration for TargetFilter.

        Attributes:
            model (Model): The Target model to filter
            fields (dict): Available filter fields and their matching options
        """

        model = Target
        fields = {
            "project": ["exact"],
            "target": ["exact", "icontains"],
            "type": ["exact"],
            "defectdojo_sync": ["exact"],
        }

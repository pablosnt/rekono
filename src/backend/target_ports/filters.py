"""Django filters for target port management.

Filter classes for querying and filtering target port objects in the REST API.
Provides field-based filtering capabilities for target port searches.
"""

from django_filters.filters import ModelChoiceFilter
from django_filters.rest_framework import FilterSet

from projects.models import Project
from target_ports.models import TargetPort


class TargetPortFilter(FilterSet):
    """Filter class for TargetPort model.

    Provides filtering capabilities for target port queries based on project,
    target, port number, and path with various matching options.

    Attributes:
        project (ModelChoiceFilter): Filter by project through target relationship
    """

    project = ModelChoiceFilter(queryset=Project.objects.all(), field_name="target__project")

    class Meta:
        """Meta configuration for TargetPortFilter.

        Attributes:
            model (Model): The TargetPort model to filter
            fields (dict): Available filter fields and their matching options
        """

        model = TargetPort
        fields = {"target": ["exact"], "port": ["exact"], "path": ["exact", "icontains"]}

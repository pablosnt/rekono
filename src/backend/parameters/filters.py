"""Django filters for input parameters REST API endpoints.

Provides filtering capabilities for parameter API queries including
project and target based filtering with text-based search options.
"""

from django_filters.rest_framework import FilterSet

from parameters.framework.filters import InputParameterFilter
from parameters.models import InputTechnology, InputVulnerability


class InputTechnologyFilter(InputParameterFilter):
    """Filter class for InputTechnology model queries.

    Provides filtering options for technology parameter API endpoints with support
    for project and target filtering along with name and version search.
    """

    class Meta:
        """Meta configuration for the InputTechnologyFilter.

        Attributes:
            model (Model): The InputTechnology model to filter
            fields (dict): Field names and their supported filter operations
        """

        model = InputTechnology
        fields = {"tasks": ["exact"], "name": ["exact", "icontains"], "version": ["exact", "icontains"]}


class InputVulnerabilityFilter(InputParameterFilter):
    """Filter class for InputVulnerability model queries.

    Provides filtering options for vulnerability parameter API endpoints with support
    for project and target filtering along with CVE identifier search.
    """

    class Meta:
        """Meta configuration for the InputVulnerabilityFilter.

        Attributes:
            model (Model): The InputVulnerability model to filter
            fields (dict): Field names and their supported filter operations
        """

        model = InputVulnerability
        fields = {"tasks": ["exact"], "cve": ["exact"]}

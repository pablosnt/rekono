"""Filters of the input parameter endpoints."""

from parameters.framework.filters import InputParameterFilter
from parameters.models import InputTechnology, InputVulnerability


class InputTechnologyFilter(InputParameterFilter):
    """Filters to search the technologies that the users provide."""

    class Meta:
        """Filter configuration for the input technologies."""

        model = InputTechnology
        fields = {"tasks": ["exact"], "name": ["exact", "icontains"], "version": ["exact", "icontains"]}


class InputVulnerabilityFilter(InputParameterFilter):
    """Filters to search the vulnerabilities that the users provide."""

    class Meta:
        """Filter configuration for the input vulnerabilities."""

        model = InputVulnerability
        fields = {"tasks": ["exact"], "cve": ["exact"]}

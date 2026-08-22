"""Viewsets of the input parameter endpoints."""

from parameters.filters import InputTechnologyFilter, InputVulnerabilityFilter
from parameters.framework.views import InputParameterViewSet
from parameters.models import InputTechnology, InputVulnerability
from parameters.serializers import (
    InputTechnologySerializer,
    InputVulnerabilitySerializer,
)


class InputTechnologyViewSet(InputParameterViewSet):
    """Read and create the technologies that the users provide as input.

    Attributes:
        queryset: All the technologies, filtered later by project membership.
        serializer_class: Serializer of the input technologies.
        filterset_class: Filters of the input technologies.
        search_fields: Free text search over the technology and its version.
        ordering_fields: Fields that the technologies can be sorted by.
    """

    queryset = InputTechnology.objects.all()
    serializer_class = InputTechnologySerializer
    filterset_class = InputTechnologyFilter
    search_fields = ["name", "version"]
    ordering_fields = ["id", "name"]


class InputVulnerabilityViewSet(InputParameterViewSet):
    """Read and create the vulnerabilities that the users provide as input.

    Attributes:
        queryset: All the vulnerabilities, filtered later by project membership.
        serializer_class: Serializer of the input vulnerabilities.
        filterset_class: Filters of the input vulnerabilities.
        search_fields: Free text search over the CVE identifier.
        ordering_fields: Fields that the vulnerabilities can be sorted by.
    """

    queryset = InputVulnerability.objects.all()
    serializer_class = InputVulnerabilitySerializer
    filterset_class = InputVulnerabilityFilter
    search_fields = ["cve"]
    ordering_fields = ["id", "cve"]

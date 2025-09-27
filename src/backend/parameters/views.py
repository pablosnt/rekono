"""Django REST framework views for input parameters management.

Provides REST API endpoints for managing input parameters including
technology specifications and vulnerability references with search and filtering capabilities.
"""

from parameters.filters import InputTechnologyFilter, InputVulnerabilityFilter
from parameters.framework.views import InputParameterViewSet
from parameters.models import InputTechnology, InputVulnerability
from parameters.serializers import (
    InputTechnologySerializer,
    InputVulnerabilitySerializer,
)


class InputTechnologyViewSet(InputParameterViewSet):
    """ViewSet for managing technology input parameters.

    Provides REST API endpoints for technology parameter CRUD operations
    with search and filtering capabilities based on name and version.

    Attributes:
        queryset (QuerySet): All InputTechnology objects
        serializer_class (Serializer): Technology parameter serializer
        filterset_class (FilterSet): Technology parameter filter
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
    """

    queryset = InputTechnology.objects.all()
    serializer_class = InputTechnologySerializer
    filterset_class = InputTechnologyFilter
    # Fields used to search input technologies
    search_fields = ["name", "version"]
    ordering_fields = ["id", "name"]


class InputVulnerabilityViewSet(InputParameterViewSet):
    """ViewSet for managing vulnerability input parameters.

    Provides REST API endpoints for vulnerability parameter CRUD operations
    with search and filtering capabilities based on CVE identifiers.

    Attributes:
        queryset (QuerySet): All InputVulnerability objects
        serializer_class (Serializer): Vulnerability parameter serializer
        filterset_class (FilterSet): Vulnerability parameter filter
        search_fields (list): Fields that can be searched
        ordering_fields (list): Fields that can be used for ordering
    """

    queryset = InputVulnerability.objects.all()
    serializer_class = InputVulnerabilitySerializer
    filterset_class = InputVulnerabilityFilter
    # Fields used to search input vulnerabilities
    search_fields = ["cve"]
    ordering_fields = ["id", "cve"]

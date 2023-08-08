from framework.views import BaseViewSet
from parameters.filters import InputTechnologyFilter, InputVulnerabilityFilter
from parameters.models import InputTechnology, InputVulnerability
from parameters.serializers import (
    InputTechnologySerializer,
    InputVulnerabilitySerializer,
)

# Create your views here.


class InputTechnologyViewSet(BaseViewSet):
    """InputTechnology ViewSet that includes: get, retrieve, create, and delete features."""

    queryset = InputTechnology.objects.all()
    serializer_class = InputTechnologySerializer
    filterset_class = InputTechnologyFilter
    # Fields used to search input technologies
    search_fields = ["name", "version"]
    ordering_fields = ["id", "target", "name"]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]

    # Project members field used for authorization purposes
    # members_field = 'target__project__members'


class InputVulnerabilityViewSet(BaseViewSet):
    """InputVulnerability ViewSet that includes: get, retrieve, create, and delete features."""

    queryset = InputVulnerability.objects.all()
    serializer_class = InputVulnerabilitySerializer
    filterset_class = InputVulnerabilityFilter
    # Fields used to search input vulnerabilities
    search_fields = ["cve"]
    ordering_fields = ["id", "target", "cve"]
    http_method_names = [
        "get",
        "post",
        "delete",
    ]

    # Project members field used for authorization purposes
    # members_field = "target__project__members"

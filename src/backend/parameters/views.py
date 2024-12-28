from parameters.filters import InputTechnologyFilter, InputVulnerabilityFilter
from parameters.framework.views import InputParameterViewSet
from parameters.models import InputTechnology, InputVulnerability
from parameters.serializers import (
    InputTechnologySerializer,
    InputVulnerabilitySerializer,
)

# Create your views here.


class InputTechnologyViewSet(InputParameterViewSet):

    queryset = InputTechnology.objects.all()
    serializer_class = InputTechnologySerializer
    filterset_class = InputTechnologyFilter
    # Fields used to search input technologies
    search_fields = ["name", "version"]
    ordering_fields = ["id", "name"]


class InputVulnerabilityViewSet(InputParameterViewSet):

    queryset = InputVulnerability.objects.all()
    serializer_class = InputVulnerabilitySerializer
    filterset_class = InputVulnerabilityFilter
    # Fields used to search input vulnerabilities
    search_fields = ["cve"]
    ordering_fields = ["id", "cve"]

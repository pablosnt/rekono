from api.views import CreateViewSet, GetViewSet
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)

from parameters.filters import InputTechnologyFilter, InputVulnerabilityFilter
from parameters.models import InputTechnology, InputVulnerability
from parameters.serializers import (InputTechnologySerializer,
                                    InputVulnerabilitySerializer)

# Create your views here.


class InputTechnologyViewSet(
    GetViewSet,
    CreateViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    '''InputTechnology ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = InputTechnology.objects.all().order_by('-id')
    serializer_class = InputTechnologySerializer
    filterset_class = InputTechnologyFilter
    # Fields used to search input technologies
    search_fields = ['name', 'version']
    # Project members field used for authorization purposes
    members_field = 'target__project__members'


class InputVulnerabilityViewSet(
    GetViewSet,
    CreateViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    '''InputVulnerability ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = InputVulnerability.objects.all().order_by('-id')
    serializer_class = InputVulnerabilitySerializer
    filterset_class = InputVulnerabilityFilter
    # Fields used to search input vulnerabilities
    search_fields = ['cve']
    # Project members field used for authorization purposes
    members_field = 'target__project__members'

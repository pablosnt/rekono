from api.views import CreateViewSet, GetViewSet
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)

from targets.filters import (TargetFilter, TargetPortFilter,
                             TargetTechnologyFilter, TargetVulnerabilityFilter)
from targets.models import (Target, TargetPort, TargetTechnology,
                            TargetVulnerability)
from targets.serializers import (TargetPortSerializer, TargetSerializer,
                                 TargetTechnologySerializer,
                                 TargetVulnerabilitySerializer)

# Create your views here.


class TargetViewSet(
    GetViewSet,
    CreateViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    '''Target ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = Target.objects.all().order_by('-id')
    serializer_class = TargetSerializer
    filterset_class = TargetFilter
    # Fields used to search targets
    search_fields = ['target']
    # Project members field used for authorization purposes
    members_field = 'project__members'


class TargetPortViewSet(
    GetViewSet,
    CreateViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    '''TargetPort ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = TargetPort.objects.all().order_by('-id')
    serializer_class = TargetPortSerializer
    filterset_class = TargetPortFilter
    # Fields used to search target ports
    search_fields = ['port']
    # Project members field used for authorization purposes
    members_field = 'target__project__members'


class TargetTechnologyViewSet(
    GetViewSet,
    CreateViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    '''TargetTechnology ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = TargetTechnology.objects.all().order_by('-id')
    serializer_class = TargetTechnologySerializer
    filterset_class = TargetTechnologyFilter
    # Fields used to search target technologies
    search_fields = ['name', 'version']
    # Project members field used for authorization purposes
    members_field = 'target_port__target__project__members'


class TargetVulnerabilityViewSet(
    GetViewSet,
    CreateViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    '''TargetVulnerability ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = TargetVulnerability.objects.all().order_by('-id')
    serializer_class = TargetVulnerabilitySerializer
    filterset_class = TargetVulnerabilityFilter
    # Fields used to search target endpoints
    search_fields = ['cve']
    # Project members field used for authorization purposes
    members_field = 'target_port__target__project__members'

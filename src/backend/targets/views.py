from api.views import CreateViewSet, GetViewSet
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)

from targets.filters import TargetFilter, TargetPortFilter
from targets.models import Target, TargetPort
from targets.serializers import TargetPortSerializer, TargetSerializer

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

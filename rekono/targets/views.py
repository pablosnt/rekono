from django.core.exceptions import PermissionDenied
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.viewsets import GenericViewSet
from targets.filters import (TargetEndpointFilter, TargetFilter,
                             TargetPortFilter)
from targets.models import Target, TargetEndpoint, TargetPort
from targets.serializers import (TargetEndpointSerializer,
                                 TargetPortSerializer, TargetSerializer)

# Create your views here.


class TargetViewSet(
    GenericViewSet,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    filterset_class = TargetFilter
    project_members_field = 'project__members'

    def get_project_members(self, data):
        return data.get('project').members.all()

    def get_queryset(self):
        project_filter = {self.project_members_field: self.request.user}
        return super().get_queryset().filter(project_filter)

    def perform_create(self, serializer):
        if self.request.user not in self.get_project_members(serializer.validated_data):
            raise PermissionDenied()
        super().perform_create(serializer)


class TargetPortViewSet(TargetViewSet):
    queryset = TargetPort.objects.all()
    serializer_class = TargetPortSerializer
    filterset_class = TargetPortFilter
    project_members_field = 'target__project__members'
    
    def get_project_members(self, data):
        return data.get('target').project.members.all()


class TargetEndpointViewSet(TargetViewSet):
    queryset = TargetEndpoint.objects.all()
    serializer_class = TargetEndpointSerializer
    filterset_class = TargetEndpointFilter
    project_members_field = 'target_port__target__project__members'

    def get_project_members(self, data):
        return data.get('target_port').target.project.members.all()

from typing import Any, Dict

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from targets.filters import (TargetEndpointFilter, TargetFilter,
                             TargetPortFilter)
from targets.models import Target, TargetEndpoint, TargetPort
from targets.serializers import (TargetEndpointSerializer,
                                 TargetPortSerializer, TargetSerializer)

# Create your views here.


class TargetViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):
    '''Target ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    filterset_class = TargetFilter
    # Fields used to search targets
    search_fields = ['target', 'target_ports__port', 'target_ports__target_endpoints__endpoint']
    # Project members field used for authorization purposes
    project_members_field = 'project__members'

    def get_project_members(self, data: Dict[str, Any]) -> QuerySet:
        '''Get project members from serializer validated data.

        Args:
            data (Dict[str, Any]): Validated data from serializer

        Returns:
            QuerySet: Project members related to the instance
        '''
        return data['project'].members.all()

    def get_queryset(self) -> QuerySet:
        '''Get the queryset that the user is allowed to get, based on project members.

        Returns:
            QuerySet: Queryset
        '''
        project_filter = {self.project_members_field: self.request.user}
        return super().get_queryset().filter(**project_filter)

    def perform_create(self, serializer: Serializer) -> None:
        '''Create a new instance using a serializer.

        Args:
            serializer (Serializer): Serializer to use in the instance creation
        '''
        if self.request.user not in self.get_project_members(serializer.validated_data):
            raise PermissionDenied()
        super().perform_create(serializer)


class TargetPortViewSet(TargetViewSet):
    '''TargetPort ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = TargetPort.objects.all()
    serializer_class = TargetPortSerializer
    filterset_class = TargetPortFilter
    # Fields used to search target ports
    search_fields = ['target__target', 'port', 'target_endpoints__endpoint']
    # Project members field used for authorization purposes
    project_members_field = 'target__project__members'

    def get_project_members(self, data: Dict[str, Any]) -> QuerySet:
        '''Get project members from serializer validated data.

        Args:
            data (Dict[str, Any]): Validated data from serializer

        Returns:
            QuerySet: Project members related to the instance
        '''
        return data['target'].project.members.all()


class TargetEndpointViewSet(TargetViewSet):
    '''TargetEndpoint ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = TargetEndpoint.objects.all()
    serializer_class = TargetEndpointSerializer
    filterset_class = TargetEndpointFilter
    # Fields used to search target endpoints
    search_fields = ['target_port__target__target', 'target_port__port', 'endpoint']
    # Project members field used for authorization purposes
    project_members_field = 'target_port__target__project__members'

    def get_project_members(self, data: Dict[str, Any]) -> QuerySet:
        '''Get project members from serializer validated data.

        Args:
            data (Dict[str, Any]): Validated data from serializer

        Returns:
            QuerySet: Project members related to the instance
        '''
        return data['target_port'].target.project.members.all()

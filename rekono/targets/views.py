from typing import Any, Dict

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin)
from rest_framework.viewsets import GenericViewSet

from targets.filters import (TargetCredentialFilter, TargetFilter,
                             TargetPortFilter, TargetTechnologyFilter,
                             TargetVulnerabilityFilter)
from targets.models import (Target, TargetCredential, TargetPort,
                            TargetTechnology, TargetVulnerability)
from targets.serializers import (TargetCredentialSerializer,
                                 TargetPortSerializer, TargetSerializer,
                                 TargetTechnologySerializer,
                                 TargetVulnerabilitySerializer)

# Create your views here.


class TargetViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):
    '''Target ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = Target.objects.all().order_by('-id')
    serializer_class = TargetSerializer
    filterset_class = TargetFilter
    # Fields used to search targets
    search_fields = ['target']
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

    def perform_create(self, serializer: TargetSerializer) -> None:
        '''Create a new instance using a serializer.

        Args:
            serializer (TargetSerializer): Serializer to use in the instance creation
        '''
        if self.request.user not in self.get_project_members(serializer.validated_data):
            # Current user can't create a new target in this project
            raise PermissionDenied()
        super().perform_create(serializer)


class TargetPortViewSet(TargetViewSet):
    '''TargetPort ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = TargetPort.objects.all().order_by('-id')
    serializer_class = TargetPortSerializer
    filterset_class = TargetPortFilter
    # Fields used to search target ports
    search_fields = ['port']
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


class TargetTechnologyViewSet(TargetViewSet):
    '''TargetTechnology ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = TargetTechnology.objects.all().order_by('-id')
    serializer_class = TargetTechnologySerializer
    filterset_class = TargetTechnologyFilter
    # Fields used to search target technologies
    search_fields = ['target_port__target__target', 'target_port__port', 'name', 'version']
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


class TargetVulnerabilityViewSet(TargetViewSet):
    '''TargetVulnerability ViewSet that includes: get, retrieve, create, and delete features.'''

    queryset = TargetVulnerability.objects.all().order_by('-id')
    serializer_class = TargetVulnerabilitySerializer
    filterset_class = TargetVulnerabilityFilter
    # Fields used to search target endpoints
    search_fields = ['target_port__target__target', 'target_port__port', 'cve']
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


class TargetCredentialViewSet(TargetViewSet):

    queryset = TargetCredential.objects.all().order_by('-id')
    serializer_class = TargetCredentialSerializer
    filterset_class = TargetCredentialFilter
    search_fields = ['target_port__target__target', 'target_port__port', 'name', 'type']
    project_members_field = 'target_port__target__project__members'

    def get_project_members(self, data: Dict[str, Any]) -> QuerySet:
        '''Get project members from serializer validated data.

        Args:
            data (Dict[str, Any]): Validated data from serializer

        Returns:
            QuerySet: Project members related to the instance
        '''
        return data['target_port'].target.project.members.all()

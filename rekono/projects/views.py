from typing import List, Type

from defectdojo.views import DefectDojoFindings, DefectDojoScans
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from executions.models import Execution
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Finding, Host, Technology, Vulnerability)
from projects.filters import ProjectFilter
from projects.models import Project
from projects.serializers import ProjectMemberSerializer, ProjectSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from tasks.enums import Status
from users.models import User

# Create your views here.


class ProjectViewSet(ModelViewSet, DefectDojoScans, DefectDojoFindings):
    '''Project ViewSet that includes: get, retrieve, create, update, delete and import Defect-Dojo features.'''

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    search_fields = ['name', 'description']                                     # Fields used to search projects
    http_method_names = ['get', 'post', 'put', 'delete']                        # Required to remove PATCH method

    def get_queryset(self) -> QuerySet:
        '''Get the Execution queryset that the user is allowed to get, based on project members.

        Returns:
            QuerySet: Execution queryset
        '''
        return super().get_queryset().filter(members=self.request.user)

    def perform_create(self, serializer: ProjectSerializer) -> None:
        '''Create a new instance using a serializer.

        Args:
            serializer (ProjectSerializer): Serializer to use in the instance creation
        '''
        serializer.save(owner=self.request.user)                                # Include current user as owner

    def get_executions(self) -> List[Execution]:
        '''Get executions list associated to the current instance. Needed for Defect-Dojo integration.

        Returns:
            List[Execution]: Executions list associated to the current instance
        '''
        return list(Execution.objects.filter(task__target__project=self.get_object(), status=Status.COMPLETED).all())

    def get_findings(self) -> List[Finding]:
        '''Get findings list associated to the current instance. Needed for Defect-Dojo integration.

        Returns:
            List[Finding]: Findings list associated to the current instance
        '''
        project = self.get_object()
        findings: List[Finding] = []
        finding_models: List[Type[Finding]] = [
            OSINT, Host, Enumeration, Technology, Endpoint, Vulnerability, Credential, Exploit
        ]
        for find_model in finding_models:
            # Search active findings related to this project
            findings.extend(list(find_model.objects.filter(
                execution__task__target__project=project,
                is_active=True
            ).all()))
        return findings

    @extend_schema(request=ProjectMemberSerializer, responses={201: ProjectMemberSerializer})
    @action(detail=True, methods=['POST'], url_path='members', url_name='members')
    def add_project_member(self, request: Request, pk: int) -> Response:
        '''Add user to the project members.

        Args:
            request (Request): Received HTTP request
            pk (int): Instance Id

        Returns:
            Response: HTTP Response
        '''
        project = self.get_object()
        serializer = ProjectMemberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.update(project, serializer.validated_data)           # Add project member
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)               # User not found
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'], url_path='members/(?P<member_id>[0-9])', url_name='delete_member')
    def delete_project_member(self, request: Request, member_id: int, pk: int) -> Response:
        '''Remove user from the project members.

        Args:
            request (Request): Received HTTP request
            member_id (int): User Id to be removed
            pk (int): Instance Id

        Returns:
            Response: HTTP Response
        '''
        project = self.get_object()
        member = get_object_or_404(project.members, pk=member_id)               # Get member from project members
        if member and member_id != project.owner.id:
            # Member found and it isn't the project owner
            project.members.remove(member)                                      # Remove project member
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

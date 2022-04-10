from typing import Type, cast

from defectdojo.exceptions import DefectDojoException
from defectdojo.reporter import report
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from executions.models import Execution
from findings.models import (OSINT, Credential, Exploit, Finding, Host, Path,
                             Port, Technology, Vulnerability)
from projects.filters import ProjectFilter
from projects.models import Project
from projects.serializers import (DefectDojoIntegrationSerializer,
                                  DefectDojoSyncSerializer,
                                  ProjectMemberSerializer, ProjectSerializer)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import User

# Create your views here.


class ProjectViewSet(ModelViewSet):
    '''Project ViewSet that includes: get, retrieve, create, update, delete and Defect-Dojo features.'''

    queryset = Project.objects.all().order_by('-id')
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

    @extend_schema(request=ProjectMemberSerializer, responses={201: None})
    @action(detail=True, methods=['POST'], url_path='members', url_name='members')
    def add_project_member(self, request: Request, pk: str) -> Response:
        '''Add user to the project members.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        '''
        project = self.get_object()
        serializer = ProjectMemberSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.update(project, serializer.validated_data)           # Add project member
                return Response(status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)               # User not found
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'], url_path='members/(?P<member_id>[0-9])', url_name='delete_member')
    def delete_project_member(self, request: Request, member_id: str, pk: str) -> Response:
        '''Remove user from the project members.

        Args:
            request (Request): Received HTTP request
            member_id (str): User Id to be removed
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        '''
        project = self.get_object()
        member = get_object_or_404(project.members, pk=member_id)               # Get member from project members
        if int(member_id) != project.owner.id:
            # Member found and it isn't the project owner
            project.members.remove(member)                                      # Remove project member
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=DefectDojoIntegrationSerializer, responses={200: Project})
    @action(detail=True, methods=['PUT'], url_path='defect-dojo/integration', url_name='defect-dojo-integration')
    def defect_dojo_integration(self, request: Request, pk: str) -> Response:
        '''Configure Defect-Dojo integration for the project.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        '''
        project = self.get_object()
        serializer = DefectDojoIntegrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.update(project, serializer.validated_data)           # Update Defect-Dojo configuration
                return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)
            except DefectDojoException as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)    # Error in Defect-Dojo requests
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=DefectDojoSyncSerializer, responses={200: Project})
    @action(detail=True, methods=['PUT'], url_path='defect-dojo/sync', url_name='defect-dojo-sync')
    def defect_dojo_synchronization(self, request: Request, pk: str) -> Response:
        '''Enable or disable Defect-Dojo synchronization for the project.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        '''
        project = self.get_object()
        serializer = DefectDojoSyncSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.update(project, serializer.validated_data)           # Update Defect-Dojo synchronization
                return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)
            except DefectDojoException as ex:
                # Defect-Dojo integration is not configured
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], url_path='defect-dojo', url_name='defect-dojo')
    def defect_dojo(self, request: Request, pk: str) -> Response:
        '''Enable or disable Defect-Dojo synchronization for the project.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        '''
        project: Project = self.get_object()
        # Get executions not reported to Defect-Dojo
        executions = Execution.objects.filter(task__target__project=project, imported_in_defectdojo=False)
        for execution in executions:                                            # For each execution
            findings = []
            for finding_model in [
                OSINT, Host, Port, Technology, Path, Vulnerability, Credential, Exploit
            ]:
                # Get related findings
                findings.extend(list(cast(Type[Finding], finding_model).objects.filter(
                    executions=execution,
                    is_active=True
                ).all()))
            try:
                report(execution, findings)                                     # Import execution in Defect-Dojo
            except DefectDojoException as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

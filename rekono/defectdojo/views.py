from typing import List

from defectdojo import uploader
from defectdojo.exceptions import DefectDojoException
from defectdojo.serializers import EngagementSerializer
from drf_spectacular.utils import extend_schema
from executions.models import Execution
from findings.models import Finding
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from security.authorization.permissions import (IsAuditor,
                                                ProjectMemberPermission)
from tasks.enums import Status


class DefectDojoScans(GenericViewSet):
    '''Base ViewSet that includes the Defect-Dojo scans import feature.'''

    def get_executions(self) -> List[Execution]:                                # pragma: no cover
        '''Get executions list associated to the current instance. To be implemented by subclasses.

        Returns:
            List[Execution]: Executions list associated to the current instance
        '''
        pass

    @extend_schema(request=EngagementSerializer, responses={200: None})
    # Permission classes are overrided to IsAuthenticated, IsAuditor and ProjectMemberPermission to allow all project
    # Auditors and Admins to make Defect-Dojo imports from their projects.
    @action(
        detail=True,
        methods=['POST'],
        url_path='defect-dojo-scans',
        url_name='defect-dojo-scans',
        permission_classes=[IsAuthenticated, IsAuditor, ProjectMemberPermission]
    )
    def defect_dojo_scans(self, request: Request, pk: str) -> Response:
        '''Import executions output in Defect-Dojo.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP Response
        '''
        # Get only the completed executions
        executions = [e for e in self.get_executions() if e.status == Status.COMPLETED]
        if not executions:                                                      # Error: no executions found
            return Response(
                {'executions': 'Incompleted executions cannot be reported to Defect-Dojo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EngagementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uploader.scans(                                                 # Import executions in Defect-Dojo
                    self.get_object().get_project(),
                    executions,
                    serializer.validated_data.get('id'),
                    serializer.validated_data.get('name'),
                    serializer.validated_data.get('description')
                )
                return Response(status=status.HTTP_200_OK)
            except DefectDojoException as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)    # Error in Defect-Dojo integration
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Error due to invalid parameters


class DefectDojoFindings(GenericViewSet):
    '''Base ViewSet that includes the Defect-Dojo findings import feature.'''

    def get_findings(self) -> List[Finding]:                                    # pragma: no cover
        '''Get findings list associated to the current instance. To be implemented by subclasses.

        Returns:
            List[Finding]: Findings list associated to the current instance
        '''
        pass

    @extend_schema(request=EngagementSerializer, responses={200: None})
    # Permission classes are overrided to IsAuthenticated, IsAuditor and ProjectMemberPermission to allow all project
    # Auditors and Admins to make Defect-Dojo imports from their projects.
    @action(
        detail=True,
        methods=['POST'],
        url_path='defect-dojo-findings',
        url_name='defect-dojo-findings',
        permission_classes=[IsAuthenticated, IsAuditor, ProjectMemberPermission]
    )
    def defect_dojo_findings(self, request: Request, pk: str) -> Response:
        '''Import findings in Defect-Dojo.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        '''
        # Get only the active findings
        findings = [f for f in self.get_findings() if f.is_active]
        if not findings:                                                        # Error: no findings found
            return Response(
                {'findings': 'Invalid findings cannot be reported to Defect-Dojo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EngagementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uploader.findings(
                    self.get_object().get_project(),
                    findings,
                    serializer.validated_data.get('id'),
                    serializer.validated_data.get('name'),
                    serializer.validated_data.get('description')
                )
                return Response(status=status.HTTP_200_OK)
            except DefectDojoException as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)    # Error in Defect-Dojo integration
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Error due to invalid parameters

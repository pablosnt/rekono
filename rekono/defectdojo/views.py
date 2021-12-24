from defectdojo import uploader
from defectdojo.exceptions import (EngagementIdNotFoundException,
                                   InvalidEngagementIdException,
                                   ProductIdNotFoundException)
from defectdojo.serializers import EngagementSerializer
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from tasks.enums import Status


class DDScansViewSet(GenericViewSet):

    def get_executions(self):
        return []

    @extend_schema(request=EngagementSerializer, responses={200: None})
    @action(
        detail=True,
        methods=['POST'],
        url_path='defect-dojo-scans',
        url_name='defect-dojo-scans'
    )
    def defect_dojo_scans(self, request, pk):
        executions = [e for e in self.get_executions() if e.status == Status.COMPLETED]
        if not executions:
            return Response(
                {'executions': 'Imcompleted executions cannot be reported to Defect-Dojo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EngagementSerializer(data=request.data)
        if serializer.is_valid() and executions:
            try:
                uploader.upload_executions(
                    executions,
                    serializer.validated_data.get('engagement_id'),
                    serializer.validated_data.get('engagement_name'),
                    serializer.validated_data.get('engagement_description')
                )
                return Response(status=status.HTTP_200_OK)
            except (
                ProductIdNotFoundException,
                EngagementIdNotFoundException,
                InvalidEngagementIdException
            ) as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DDFindingsViewSet(GenericViewSet):

    def get_findings(self):
        return []

    @extend_schema(request=EngagementSerializer, responses={200: None})
    @action(
        detail=True,
        methods=['POST'],
        url_path='defect-dojo-findings',
        url_name='defect-dojo-findings'
    )
    def defect_dojo_findings(self, request, pk):
        findings = [f for f in self.get_findings() if f.is_active]
        if not findings:
            return Response(
                {'findings': 'Invalid findings cannot be reported to Defect-Dojo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EngagementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uploader.upload_findings(
                    findings,
                    serializer.validated_data.get('engagement_id'),
                    serializer.validated_data.get('engagement_name'),
                    serializer.validated_data.get('engagement_description')
                )
                return Response(status=status.HTTP_200_OK)
            except (
                ProductIdNotFoundException,
                EngagementIdNotFoundException,
                InvalidEngagementIdException
            ) as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

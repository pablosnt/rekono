from defectdojo import uploader
from defectdojo.exceptions import (EngagementIdNotFoundException,
                                   InvalidEngagementIdException,
                                   ProductIdNotFoundException)
from defectdojo.serializers import EngagementSerializer
from drf_spectacular.utils import extend_schema
from executions.filters import ExecutionFilter
from executions.models import Execution
from executions.serializers import ExecutionSerializer
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

# Create your views here.


class ExecutionViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Execution.objects.all()
    serializer_class = ExecutionSerializer
    filterset_class = ExecutionFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(task__target__project__members=self.request.user)

    @extend_schema(request=EngagementSerializer, responses={200: None})
    @action(
        detail=True,
        methods=['POST'],
        url_path='defect-dojo-scans',
        url_name='defect-dojo-scans'
    )
    def defect_dojo_scans(self, request, pk):
        execution = self.get_object()
        serializer = EngagementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uploader.upload_executions(
                    [execution],
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

    @extend_schema(request=EngagementSerializer, responses={200: None})
    @action(
        detail=True,
        methods=['POST'],
        url_path='defect-dojo-findings',
        url_name='defect-dojo-findingss'
    )
    def defect_dojo_findings(self, request, pk):
        execution = self.get_object()
        serializer = EngagementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                findings = []
                for find_model in [
                    OSINT, Host, Enumeration, Technology,
                    Endpoint, Vulnerability, Credential, Exploit
                ]:
                    findings.extend(find_model.objects.filter(
                        execution=execution,
                        is_active=True
                    ).all())
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

from defectdojo import uploader
from defectdojo.exceptions import (EngagementIdNotFoundException,
                                   InvalidEngagementIdException,
                                   ProductIdNotFoundException)
from defectdojo.serializers import EngagementSerializer
from drf_spectacular.utils import extend_schema
from findings.enums import DataType
from findings.filters import (CredentialFilter, EndpointFilter,
                              EnumerationFilter, ExploitFilter, HostFilter,
                              OSINTFilter, TechnologyFilter,
                              VulnerabilityFilter)
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Host, Technology, Vulnerability)
from findings.serializers import (CredentialSerializer, EndpointSerializer,
                                  EnumerationSerializer, ExploitSerializer,
                                  HostSerializer, OSINTSerializer,
                                  TechnologySerializer,
                                  VulnerabilitySerializer)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from targets.serializers import TargetSerializer

# Create your views here.


class FindingBaseView(GenericViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(execution__task__target__project__members=self.request.user)

    def destroy(self, request, *args, **kwargs):
        finding = self.get_object()
        finding.is_active = False
        finding.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={201: None})
    @action(detail=True, methods=['POST'], url_path='enable', url_name='enable')
    def enable(self, request, pk):
        finding = self.get_object()
        finding.is_active = True
        finding.save()
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(request=EngagementSerializer, responses={200: None})
    @action(detail=True, methods=['POST'], url_path='defect-dojo', url_name='defect-dojo')
    def defect_dojo(self, request, pk):
        finding = self.get_object()
        if not finding.is_active:
            return Response(
                {'finding': 'Finding is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EngagementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uploader.upload_findings(
                    [finding],
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


class OSINTViewSet(FindingBaseView):
    queryset = OSINT.objects.all()
    serializer_class = OSINTSerializer
    filterset_class = OSINTFilter

    @extend_schema(request=None, responses={201: TargetSerializer})
    @action(detail=True, methods=['POST'], url_path='target', url_name='target')
    def target(self, request, pk):
        osint = self.get_object()
        if osint.data_type in [DataType.IP, DataType.DOMAIN]:
            serializer = TargetSerializer(data={
                'project': osint.execution.task.target.project.id,
                'target': osint.data
            })
            if serializer.is_valid():
                target = serializer.create(serializer.validated_data)
                return Response(TargetSerializer(target).data, status=status.HTTP_201_CREATED)
        return Response(
            {'data_type': 'Unsupported option for this OSINT data type'},
            status=status.HTTP_400_BAD_REQUEST
        )


class HostViewSet(FindingBaseView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    filterset_class = HostFilter


class EnumerationViewSet(FindingBaseView):
    queryset = Enumeration.objects.all()
    serializer_class = EnumerationSerializer
    filterset_class = EnumerationFilter


class EndpointViewSet(FindingBaseView):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer
    filterset_class = EndpointFilter


class TechnologyViewSet(FindingBaseView):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filterset_class = TechnologyFilter


class VulnerabilityViewSet(FindingBaseView, UpdateModelMixin):
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter
    http_method_names = ['get', 'put', 'post', 'delete']


class CredentialViewSet(FindingBaseView):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    filterset_class = CredentialFilter


class ExploitViewSet(FindingBaseView):
    queryset = Exploit.objects.all()
    serializer_class = ExploitSerializer
    filterset_class = ExploitFilter

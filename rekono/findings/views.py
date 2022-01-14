from re import search

from defectdojo.serializers import EngagementSerializer
from defectdojo.views import DefectDojoFindings
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
from targets.serializers import TargetSerializer

# Create your views here.


class FindingBaseView(ListModelMixin, RetrieveModelMixin, DestroyModelMixin, DefectDojoFindings):

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(execution__task__target__project__members=self.request.user)

    def get_findings(self):
        return [self.get_object()]

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
    def defect_dojo_findings(self, request, pk):
        return super().defect_dojo_findings(request, pk)


class OSINTViewSet(FindingBaseView):
    queryset = OSINT.objects.all()
    serializer_class = OSINTSerializer
    filterset_class = OSINTFilter
    search_fields = ['data', 'source']

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
    search_fields = [
        'address',
        'enumeration__port', 'enumeration__service',
        'enumeration__endpoint__endpoint',
        'enumeration__technology__name', 'enumeration__technology__version',
        'enumeration__vulnerability__name', 'enumeration__vulnerability__cve',
        'enumeration__vulnerability__cwe', 'enumeration__vulnerability__severity',
        'enumeration__technology__vulnerability__name',
        'enumeration__technology__vulnerability__cve',
        'enumeration__technology__vulnerability__cwe',
        'enumeration__technology__vulnerability__severity',
        'enumeration__vulnerability__exploit__name',
        'enumeration__technology__vulnerability__exploit__name'
    ]


class EnumerationViewSet(FindingBaseView):
    queryset = Enumeration.objects.all()
    serializer_class = EnumerationSerializer
    filterset_class = EnumerationFilter
    search_fields = [
        'host__address',
        'port', 'service',
        'endpoint__endpoint',
        'technology__name', 'technology__version',
        'vulnerability__name', 'vulnerability__cve',
        'vulnerability__cwe', 'vulnerability__severity',
        'technology__vulnerability__name', 'technology__vulnerability__cve',
        'technology__vulnerability__cwe', 'technology__vulnerability__severity',
        'vulnerability__exploit__name', 'technology__vulnerability__exploit__name'
    ]


class EndpointViewSet(FindingBaseView):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer
    filterset_class = EndpointFilter
    search_fields = [
        'enumeration__host__address',
        'enumeration__port', 'enumeration__service',
        'endpoint'
    ]


class TechnologyViewSet(FindingBaseView):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filterset_class = TechnologyFilter
    search_fields = [
        'enumeration__host__address',
        'enumeration__port', 'enumeration__service',
        'enumeration__endpoint__endpoint',
        'name', 'version',
        'vulnerability__name', 'vulnerability__cve',
        'vulnerability__cwe', 'vulnerability__severity',
        'vulnerability__exploit__name', 'exploit__name'
    ]


class VulnerabilityViewSet(FindingBaseView, UpdateModelMixin):
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter
    http_method_names = ['get', 'put', 'post', 'delete']
    search_fields = [
        'enumeration__host__address', 'technology__enumeration__host__address',
        'enumeration__port', 'enumeration__service',
        'technology__enumeration__port', 'technology__enumeration__service',
        'enumeration__endpoint__endpoint', 'technology__enumeration__endpoint__endpoint',
        'enumeration__technology__name', 'enumeration__technology__version',
        'technology__name', 'technology__version',
        'name', 'cve', 'cwe', 'severity',
        'exploit__name'
    ]


class CredentialViewSet(FindingBaseView):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    filterset_class = CredentialFilter
    search_fields = ['email', 'username']


class ExploitViewSet(FindingBaseView):
    queryset = Exploit.objects.all()
    serializer_class = ExploitSerializer
    filterset_class = ExploitFilter
    search_fields = [
        'vulnerability__name', 'vulnerability__cve', 'vulnerability__cwe',
        'vulnerability__enumeration__service', 'technology__vulnerability__name',
        'technology__vulnerability__cve', 'technology__vulnerability__cwe',
        'technology__enumeration__service', 'name', 'description', 'reference'
    ]
    search_fields = [
        'vulnerability__enumeration__host__address', 'technology__enumeration__host__address',
        'vulnerability__enumeration__port', 'vulnerability__enumeration__service',
        'technology__enumeration__port', 'technology__enumeration__service',
        'vulnerability__enumeration__endpoint__endpoint',
        'technology__enumeration__endpoint__endpoint',
        'enumeration__technology__name', 'enumeration__technology__version',
        'technology__name', 'technology__version',
        'vulnerability__name', 'vulnerability__cve',
        'vulnerability__cwe', 'vulnerability__severity',
        'technology__vulnerability__name', 'technology__vulnerability__cve',
        'technology__vulnerability__cwe', 'technology__vulnerability__severity',
        'name'
    ]

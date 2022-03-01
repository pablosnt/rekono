from typing import Any, List
from urllib.request import Request

from api.filters import RekonoFilterBackend
from defectdojo.serializers import EngagementSerializer
from defectdojo.views import DefectDojoFindings
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from findings.enums import DataType
from findings.filters import (CredentialFilter, EndpointFilter,
                              EnumerationFilter, ExploitFilter, HostFilter,
                              OSINTFilter, TechnologyFilter,
                              VulnerabilityFilter)
from findings.models import (OSINT, Credential, Endpoint, Enumeration, Exploit,
                             Finding, Host, Technology, Vulnerability)
from findings.serializers import (CredentialSerializer, EndpointSerializer,
                                  EnumerationSerializer, ExploitSerializer,
                                  HostSerializer, OSINTSerializer,
                                  TechnologySerializer,
                                  VulnerabilitySerializer)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.response import Response
from targets.serializers import TargetSerializer

# Create your views here.


class FindingBaseView(ListModelMixin, RetrieveModelMixin, DestroyModelMixin, DefectDojoFindings):
    '''Common finding ViewSet that includes: get, retrieve, enable, disable and import in Defect-Dojo features.'''

    # Replace DjangoFilterBackend by RekonoFilterBackend to allow filters by N-M relations like 'executions' field.
    filter_backends = [RekonoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self) -> QuerySet:
        '''Get the Finding queryset that the user is allowed to get, based on project members.

        Returns:
            QuerySet: Execution queryset
        '''
        queryset = super().get_queryset()
        return queryset.filter(executions__task__target__project__members=self.request.user)

    def get_findings(self) -> List[Finding]:
        '''Get findings list associated to the current instance. Needed for Defect-Dojo integration.

        Returns:
            List[Finding]: Findings list associated to the current instance
        '''
        return [self.get_object()]

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        '''Disable finding.

        Args:
            request (Request): Received HTTP request

        Returns:
            Response: HTTP response
        '''
        finding: Finding = self.get_object()
        finding.is_active = False
        finding.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={201: None})
    @action(detail=True, methods=['POST'], url_path='enable', url_name='enable')
    def enable(self, request: Request, pk: str) -> Response:
        '''Enable finding.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        '''
        finding: Finding = self.get_object()
        finding.is_active = True
        finding.save(update_fields=['is_active'])
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(request=EngagementSerializer, responses={200: None})
    @action(detail=True, methods=['POST'], url_path='defect-dojo', url_name='defect-dojo')
    def defect_dojo_findings(self, request, pk):
        '''Import finding in Defect-Dojo.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        '''
        return super().defect_dojo_findings(request, pk)


class OSINTViewSet(FindingBaseView):
    '''OSINT ViewSet that includes: get, retrieve, enable, disable, import in Defect-Dojo and target creation features.'''  # noqa: E501

    queryset = OSINT.objects.all().order_by('-id')
    serializer_class = OSINTSerializer
    filterset_class = OSINTFilter
    search_fields = ['data', 'source']                                          # Fields used to search OSINTs

    @extend_schema(request=None, responses={201: TargetSerializer})
    @action(detail=True, methods=['POST'], url_path='target', url_name='target')
    def target(self, request: Request, pk: str) -> Response:
        '''Target creation from OSINT data.

        Args:
            request (Request): Received HTTP request
            pk (str): Instance Id

        Returns:
            Response: HTTP response
        '''
        osint = self.get_object()
        if osint.data_type in [DataType.IP, DataType.DOMAIN]:                   # Only supported for IPs and Domains
            serializer = TargetSerializer(data={'project': osint.get_project().id, 'target': osint.data})
            if serializer.is_valid():
                target = serializer.create(serializer.validated_data)           # Target creation
                return Response(TargetSerializer(target).data, status=status.HTTP_201_CREATED)
        return Response(
            {'data_type': ['Unsupported option for this OSINT data type']}, status=status.HTTP_400_BAD_REQUEST
        )


class HostViewSet(FindingBaseView):
    '''Host ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Host.objects.all().order_by('-id')
    serializer_class = HostSerializer
    filterset_class = HostFilter
    search_fields = [                                                           # Fields used to search Hosts
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
    '''Enumeration ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Enumeration.objects.all().order_by('-id')
    serializer_class = EnumerationSerializer
    filterset_class = EnumerationFilter
    search_fields = [                                                           # Fields used to search Enumerations
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
    '''Endpoint ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Endpoint.objects.all().order_by('-id')
    serializer_class = EndpointSerializer
    filterset_class = EndpointFilter
    search_fields = [                                                           # Fields used to search Endpoints
        'enumeration__host__address',
        'enumeration__port', 'enumeration__service',
        'endpoint'
    ]


class TechnologyViewSet(FindingBaseView):
    '''Technology ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Technology.objects.all().order_by('-id')
    serializer_class = TechnologySerializer
    filterset_class = TechnologyFilter
    search_fields = [                                                           # Fields used to search Technologies
        'enumeration__host__address',
        'enumeration__port', 'enumeration__service',
        'enumeration__endpoint__endpoint',
        'name', 'version',
        'vulnerability__name', 'vulnerability__cve',
        'vulnerability__cwe', 'vulnerability__severity',
        'vulnerability__exploit__name', 'exploit__name'
    ]


class CredentialViewSet(FindingBaseView):
    '''Credential ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Credential.objects.all().order_by('-id')
    serializer_class = CredentialSerializer
    filterset_class = CredentialFilter
    # Fields used to search Credentials
    search_fields = [
        'technology__enumeration__host__address',
        'technology__enumeration__port', 'technology__enumeration__service',
        'technology__name', 'technology__version',
        'email', 'username'
    ]


class VulnerabilityViewSet(FindingBaseView):
    '''Vulnerability ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Vulnerability.objects.all().order_by('-id')
    serializer_class = VulnerabilitySerializer
    filterset_class = VulnerabilityFilter
    search_fields = [                                                           # Fields used to search Vulnerabilities
        'enumeration__host__address', 'technology__enumeration__host__address',
        'enumeration__port', 'enumeration__service',
        'technology__enumeration__port', 'technology__enumeration__service',
        'enumeration__endpoint__endpoint', 'technology__enumeration__endpoint__endpoint',
        'enumeration__technology__name', 'enumeration__technology__version',
        'technology__name', 'technology__version',
        'name', 'cve', 'cwe', 'severity',
        'exploit__name'
    ]


class ExploitViewSet(FindingBaseView):
    '''Exploit ViewSet that includes: get, retrieve, enable, disable and import Defect-Dojo features.'''

    queryset = Exploit.objects.all().order_by('-id')
    serializer_class = ExploitSerializer
    filterset_class = ExploitFilter
    search_fields = [                                                           # Fields used to search Exploits
        'vulnerability__enumeration__host__address', 'technology__enumeration__host__address',
        'vulnerability__enumeration__port', 'vulnerability__enumeration__service',
        'technology__enumeration__port', 'technology__enumeration__service',
        'vulnerability__enumeration__endpoint__endpoint',
        'technology__enumeration__endpoint__endpoint',
        'vulnerability__enumeration__technology__name', 'vulnerability__enumeration__technology__version',
        'technology__name', 'technology__version',
        'vulnerability__name', 'vulnerability__cve',
        'vulnerability__cwe', 'vulnerability__severity',
        'technology__vulnerability__name', 'technology__vulnerability__cve',
        'technology__vulnerability__cwe', 'technology__vulnerability__severity',
        'name'
    ]

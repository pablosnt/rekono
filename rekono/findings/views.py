from drf_spectacular.utils import extend_schema
from findings.models import (OSINT, Credential, Enumeration, Exploit, Host,
                             HttpEndpoint, Technology, Vulnerability)
from findings.serializers import (CredentialSerializer, EnumerationSerializer,
                                  ExploitSerializer, HostSerializer,
                                  HttpEndpointSerializer, OSINTSerializer,
                                  TechnologySerializer,
                                  VulnerabilitySerializer)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

# Create your views here.


class FindingBaseView(GenericViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            execution__task__target__project__members=self.request.user
        ).order_by('-id')

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


class OSINTViewSet(FindingBaseView):
    queryset = OSINT.objects.all()
    serializer_class = OSINTSerializer
    filterset_fields = {
        'execution': ['exact'],
        'execution__task': ['exact'],
        'execution__task__target': ['exact'],
        'execution__task__target__project': ['exact'],
        'execution__task__tool': ['exact'],
        'execution__step__tool': ['exact'],
        'execution__task__executor': ['exact'],
        'execution__start': ['gte', 'lte', 'exact'],
        'execution__end': ['gte', 'lte', 'exact'],
        'data_type': ['exact'],
        'source': ['exact', 'contains'],
        'creation': ['gte', 'lte', 'exact'],
        'is_active': ['exact'],
    }
    ordering_fields = (
        ('task', 'execution__task'),
        ('target', 'execution__task__target'),
        ('project', 'execution__task__target__project'),
        ('task__tool', 'execution__task__tool'),
        ('step__tool', 'execution__step__tool'),
        ('executor', 'execution__task__executor'),
        'execution', 'data', 'data_type', 'source', 'creation', 'is_active'
    )


class HostViewSet(FindingBaseView):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    filterset_fields = {
        'execution': ['exact'],
        'execution__task': ['exact'],
        'execution__task__target': ['exact'],
        'execution__task__target__project': ['exact'],
        'execution__task__tool': ['exact'],
        'execution__step__tool': ['exact'],
        'execution__task__executor': ['exact'],
        'execution__start': ['gte', 'lte', 'exact'],
        'execution__end': ['gte', 'lte', 'exact'],
        'address': ['exact', 'contains'],
        'os_type': ['exact'],
        'creation': ['gte', 'lte', 'exact'],
        'is_active': ['exact'],
    }
    ordering_fields = (
        ('task', 'execution__task'),
        ('target', 'execution__task__target'),
        ('project', 'execution__task__target__project'),
        ('task__tool', 'execution__task__tool'),
        ('step__tool', 'execution__step__tool'),
        ('executor', 'execution__task__executor'),
        'execution', 'address', 'os_type', 'creation', 'is_active'
    )


class EnumerationViewSet(FindingBaseView):
    queryset = Enumeration.objects.all()
    serializer_class = EnumerationSerializer
    filterset_fields = {
        'execution': ['exact'],
        'execution__task': ['exact'],
        'execution__task__target': ['exact'],
        'execution__task__target__project': ['exact'],
        'execution__task__tool': ['exact'],
        'execution__step__tool': ['exact'],
        'execution__task__executor': ['exact'],
        'execution__start': ['gte', 'lte', 'exact'],
        'execution__end': ['gte', 'lte', 'exact'],
        'host': ['exact'],
        'host__address': ['exact', 'contains'],
        'host__os_type': ['exact'],
        'port': ['exact'],
        'port_status': ['exact'],
        'protocol': ['exact'],
        'service': ['exact', 'contains'],
        'creation': ['gte', 'lte', 'exact'],
        'is_active': ['exact'],
    }
    ordering_fields = (
        ('task', 'execution__task'),
        ('target', 'execution__task__target'),
        ('project', 'execution__task__target__project'),
        ('task__tool', 'execution__task__tool'),
        ('step__tool', 'execution__step__tool'),
        ('executor', 'execution__task__executor'),
        ('os_type', 'host__os_type'),
        'execution', 'host', 'port', 'protocol', 'service', 'creation', 'is_active'
    )


class HttpEndpointViewSet(FindingBaseView):
    queryset = HttpEndpoint.objects.all()
    serializer_class = HttpEndpointSerializer
    filterset_fields = {
        'execution': ['exact'],
        'execution__task': ['exact'],
        'execution__task__target': ['exact'],
        'execution__task__target__project': ['exact'],
        'execution__task__tool': ['exact'],
        'execution__step__tool': ['exact'],
        'execution__task__executor': ['exact'],
        'execution__start': ['gte', 'lte', 'exact'],
        'execution__end': ['gte', 'lte', 'exact'],
        'enumeration': ['exact'],
        'enumeration__host': ['exact'],
        'enumeration__host__address': ['exact', 'contains'],
        'enumeration__host__os_type': ['exact'],
        'enumeration__port': ['exact'],
        'endpoint': ['exact', 'contains'],
        'status': ['exact'],
        'creation': ['gte', 'lte', 'exact'],
        'is_active': ['exact'],
    }
    ordering_fields = (
        ('task', 'execution__task'),
        ('target', 'execution__task__target'),
        ('project', 'execution__task__target__project'),
        ('task__tool', 'execution__task__tool'),
        ('step__tool', 'execution__step__tool'),
        ('executor', 'execution__task__executor'),
        ('host', 'enumeration__host'),
        'execution', 'enumeration', 'endpoint', 'status', 'creation', 'is_active'
    )


class TechnologyViewSet(FindingBaseView):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filterset_fields = {
        'execution': ['exact'],
        'execution__task': ['exact'],
        'execution__task__target': ['exact'],
        'execution__task__target__project': ['exact'],
        'execution__task__tool': ['exact'],
        'execution__step__tool': ['exact'],
        'execution__task__executor': ['exact'],
        'execution__start': ['gte', 'lte', 'exact'],
        'execution__end': ['gte', 'lte', 'exact'],
        'enumeration': ['exact'],
        'enumeration__host': ['exact'],
        'enumeration__host__address': ['exact', 'contains'],
        'enumeration__host__os_type': ['exact'],
        'enumeration__port': ['exact'],
        'name': ['exact', 'contains'],
        'version': ['exact', 'contains'],
        'related_to': ['exact'],
        'creation': ['gte', 'lte', 'exact'],
        'is_active': ['exact'],
    }
    ordering_fields = (
        ('task', 'execution__task'),
        ('target', 'execution__task__target'),
        ('project', 'execution__task__target__project'),
        ('task__tool', 'execution__task__tool'),
        ('step__tool', 'execution__step__tool'),
        ('executor', 'execution__task__executor'),
        ('host', 'enumeration__host'),
        'execution', 'enumeration', 'name', 'version', 'creation', 'is_active'
    )


class VulnerabilityViewSet(FindingBaseView, UpdateModelMixin):
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer
    filterset_fields = {
        'execution': ['exact'],
        'execution__task': ['exact'],
        'execution__task__target': ['exact'],
        'execution__task__target__project': ['exact'],
        'execution__task__tool': ['exact'],
        'execution__step__tool': ['exact'],
        'execution__task__executor': ['exact'],
        'execution__start': ['gte', 'lte', 'exact'],
        'execution__end': ['gte', 'lte', 'exact'],
        'technology': ['exact'],
        'technology__name': ['exact', 'contains'],
        'technology__version': ['exact', 'contains'],
        'technology__enumeration': ['exact'],
        'technology__enumeration__host': ['exact'],
        'technology__enumeration__host__address': ['exact', 'contains'],
        'technology__enumeration__host__os_type': ['exact'],
        'technology__enumeration__port': ['exact'],
        'name': ['exact', 'contains'],
        'description': ['exact', 'contains'],
        'severity': ['exact'],
        'cve': ['exact', 'contains'],
        'creation': ['gte', 'lte', 'exact'],
        'is_active': ['exact'],
    }
    ordering_fields = (
        ('task', 'execution__task'),
        ('target', 'execution__task__target'),
        ('project', 'execution__task__target__project'),
        ('task__tool', 'execution__task__tool'),
        ('step__tool', 'execution__step__tool'),
        ('executor', 'execution__task__executor'),
        ('host', 'enumeration__host'),
        'execution', 'enumeration', 'technology', 'name', 'severity', 'cve', 'creation', 'is_active'
    )
    http_method_names = ['get', 'put', 'post', 'delete']


class CredentialViewSet(FindingBaseView):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    filterset_fields = {
        'execution': ['exact'],
        'execution__task': ['exact'],
        'execution__task__target': ['exact'],
        'execution__task__target__project': ['exact'],
        'execution__task__tool': ['exact'],
        'execution__step__tool': ['exact'],
        'execution__task__executor': ['exact'],
        'execution__start': ['gte', 'lte', 'exact'],
        'execution__end': ['gte', 'lte', 'exact'],
        'email': ['exact', 'contains'],
        'username': ['exact', 'contains'],
        'creation': ['gte', 'lte', 'exact'],
        'is_active': ['exact'],
    }
    ordering_fields = (
        ('task', 'execution__task'),
        ('target', 'execution__task__target'),
        ('project', 'execution__task__target__project'),
        ('task__tool', 'execution__task__tool'),
        ('step__tool', 'execution__step__tool'),
        ('executor', 'execution__task__executor'),
        'email', 'username', 'creation', 'is_active'
    )


class ExploitViewSet(FindingBaseView):
    queryset = Exploit.objects.all()
    serializer_class = ExploitSerializer
    filterset_fields = {
        'execution': ['exact'],
        'execution__task': ['exact'],
        'execution__task__target': ['exact'],
        'execution__task__target__project': ['exact'],
        'execution__task__tool': ['exact'],
        'execution__step__tool': ['exact'],
        'execution__task__executor': ['exact'],
        'execution__start': ['gte', 'lte', 'exact'],
        'execution__end': ['gte', 'lte', 'exact'],
        'vulnerability__technology': ['exact'],
        'vulnerability__technology__name': ['exact', 'contains'],
        'vulnerability__technology__version': ['exact', 'contains'],
        'vulnerability__technology__enumeration': ['exact'],
        'vulnerability__technology__enumeration__host': ['exact'],
        'vulnerability__technology__enumeration__host__address': ['exact', 'contains'],
        'vulnerability__technology__enumeration__host__os_type': ['exact'],
        'vulnerability__technology__enumeration__port': ['exact'],
        'technology': ['exact'],
        'technology__name': ['exact', 'contains'],
        'technology__version': ['exact', 'contains'],
        'technology__enumeration': ['exact'],
        'technology__enumeration__host': ['exact'],
        'technology__enumeration__host__address': ['exact', 'contains'],
        'technology__enumeration__host__os_type': ['exact'],
        'technology__enumeration__port': ['exact'],
        'name': ['exact', 'contains'],
        'description': ['exact', 'contains'],
        'reference': ['exact', 'contains'],
        'checked': ['exact'],
        'creation': ['gte', 'lte', 'exact'],
        'is_active': ['exact'],
    }
    ordering_fields = (
        ('task', 'execution__task'),
        ('target', 'execution__task__target'),
        ('project', 'execution__task__target__project'),
        ('task__tool', 'execution__task__tool'),
        ('step__tool', 'execution__step__tool'),
        ('executor', 'execution__task__executor'),
        ('host', 'enumeration__host'),
        'execution', 'enumeration', 'technology', 'name', 'creation', 'is_active'
    )

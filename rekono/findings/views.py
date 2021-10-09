from rest_framework.views import APIView
from findings.models import (OSINT, Enumeration, Exploit, Host, HttpEndpoint,
                             Technology, Vulnerability)
from findings.serializers import (EnumerationSerializer, ExploitSerializer,
                                  HostSerializer, HttpEndpointSerializer,
                                  OSINTSerializer, TechnologySerializer,
                                  VulnerabilitySerializer)
from rest_framework import status
from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


class FindingDisableMixin(DestroyModelMixin):

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.queryset.get(pk=kwargs.get('pk'), is_active=True)
            instance.is_active = False
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FindingEnableView(APIView):

    def post(self, request, pk):
        try:
            instance = self.queryset.get(pk=pk, is_active=False)
            instance.is_active = True
            instance.save()
            return Response(status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class OSINTViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
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


class OSINTEnableView(FindingEnableView):
    queryset = OSINT.objects.all()
    serializer_class = None


class HostViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
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


class HostEnableView(FindingEnableView):
    queryset = Host.objects.all()
    serializer_class = None


class EnumerationViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
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


class EnumerationEnableView(FindingEnableView):
    queryset = Enumeration.objects.all()
    serializer_class = None


class HttpEndpointViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
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


class HttpEndpointEnableView(FindingEnableView):
    queryset = HttpEndpoint.objects.all()
    serializer_class = None


class TechnologyViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
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


class TechnologyEnableView(FindingEnableView):
    queryset = Technology.objects.all()
    serializer_class = None


class VulnerabilityViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    FindingDisableMixin
):
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
    http_method_names = ['get', 'put', 'delete']


class VulnerabilityEnableView(FindingEnableView):
    queryset = Vulnerability.objects.all()
    serializer_class = None


class ExploitViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
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


class ExploitEnableView(FindingEnableView):
    queryset = Exploit.objects.all()
    serializer_class = None

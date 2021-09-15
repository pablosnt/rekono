from findings.models import (OSINT, Enumeration, Exploit, Host, HttpEndpoint,
                             Technology, Vulnerability)
from findings.serializers import (EnumerationSerializer, ExploitSerializer,
                                  HostSerializer, HttpEndpointSerializer,
                                  OSINTSerializer, TechnologySerializer,
                                  VulnerabilitySerializer)
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

# Create your views here.


class OSINTViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = OSINT.objects.all()
    serializer_class = OSINTSerializer


class HostViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Host.objects.all()
    serializer_class = HostSerializer


class EnumerationViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Enumeration.objects.all()
    serializer_class = EnumerationSerializer


class HttpEndpointViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = HttpEndpoint.objects.all()
    serializer_class = HttpEndpointSerializer


class TechnologyViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer


class VulnerabilityViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer


class ExploitViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Exploit.objects.all()
    serializer_class = ExploitSerializer

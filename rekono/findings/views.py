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

    def post(self, request, pk, format=None):
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


class OSINTEnableView(FindingEnableView):
    queryset = OSINT.objects.all()


class HostViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
    queryset = Host.objects.all()
    serializer_class = HostSerializer


class HostEnableView(FindingEnableView):
    queryset = Host.objects.all()


class EnumerationViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
    queryset = Enumeration.objects.all()
    serializer_class = EnumerationSerializer


class EnumerationEnableView(FindingEnableView):
    queryset = Enumeration.objects.all()


class HttpEndpointViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
    queryset = HttpEndpoint.objects.all()
    serializer_class = HttpEndpointSerializer


class HttpEndpointEnableView(FindingEnableView):
    queryset = HttpEndpoint.objects.all()


class TechnologyViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer


class TechnologyEnableView(FindingEnableView):
    queryset = Technology.objects.all()


class VulnerabilityViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    FindingDisableMixin
):
    queryset = Vulnerability.objects.all()
    serializer_class = VulnerabilitySerializer


class VulnerabilityEnableView(FindingEnableView):
    queryset = Vulnerability.objects.all()


class ExploitViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    FindingDisableMixin
):
    queryset = Exploit.objects.all()
    serializer_class = ExploitSerializer


class ExploitEnableView(FindingEnableView):
    queryset = Exploit.objects.all()

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from tools.filters import ConfigurationFilter, ToolFilter
from tools.models import Configuration, Tool
from tools.serializers import ConfigurationSerializer, ToolSerializer

# Create your views here.


class ToolViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    filterset_class = ToolFilter


class ConfigurationViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    filterset_class = ConfigurationFilter

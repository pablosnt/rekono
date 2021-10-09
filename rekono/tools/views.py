from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from tools.models import Configuration, Tool
from tools.serializers import ConfigurationSerializer, ToolSerializer

# Create your views here.


class ConfigurationViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    filterset_fields = {
        'tool': ['exact'],
        'tool__name': ['exact', 'contains'],
        'tool__command': ['exact', 'contains'],
        'tool__stage': ['exact'],
        'default': ['exact'],
    }


class ToolViewSet(
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin
):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    filterset_fields = {
        'name': ['exact', 'contains'],
        'command': ['exact', 'contains'],
        'stage': ['exact'],
    }

from framework.views import BaseViewSet, LikeViewSet
from tools.filters import ConfigurationFilter, ToolFilter
from tools.models import Configuration, Tool
from tools.serializers import ConfigurationSerializer, ToolSerializer

# Create your views here.


class ToolViewSet(LikeViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    filterset_class = ToolFilter
    search_fields = ["name", "command"]
    ordering_fields = ["id", "name", "command"]
    http_method_names = ["get"]


class ConfigurationViewSet(BaseViewSet):
    """Configuration ViewSet that includes: get and retrieve features."""

    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    filterset_class = ConfigurationFilter
    search_fields = ["name"]
    http_method_names = ["get"]

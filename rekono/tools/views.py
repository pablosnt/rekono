from likes.views import LikeManagementView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from tools.filters import ConfigurationFilter, ToolFilter
from tools.models import Configuration, Tool
from tools.serializers import ConfigurationSerializer, ToolSerializer

# Create your views here.


class ToolViewSet(LikeManagementView, ListModelMixin, RetrieveModelMixin):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    filterset_class = ToolFilter
    search_fields = ['name', 'command', 'configuration__name']


class ConfigurationViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    filterset_class = ConfigurationFilter
    search_fields = ['name', 'tool__command', 'tool__name']

from django.db.models import Min, QuerySet
from likes.views import LikeManagementView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from tools.filters import ConfigurationFilter, ToolFilter
from tools.models import Configuration, Tool
from tools.serializers import ConfigurationSerializer, ToolSerializer

# Create your views here.


class ToolViewSet(LikeManagementView, ListModelMixin, RetrieveModelMixin):
    '''Tool ViewSet that includes: get, retrieve, like and dislike features.'''

    queryset = Tool.objects.all().order_by('-id')
    serializer_class = ToolSerializer
    filterset_class = ToolFilter
    # Fields used to search tools
    search_fields = ['name', 'command']
    # Required to remove unneeded ProjectMemberPermission
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self) -> QuerySet:
        '''Get the model queryset. It's required for allow the access to the likes count by the child ViewSets.

        Returns:
            QuerySet: Model queryset
        '''
        return super().get_queryset().annotate(stage=Min('configurations__stage'))


class ConfigurationViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    '''Configuration ViewSet that includes: get and retrieve features.'''

    queryset = Configuration.objects.all().order_by('-id')
    serializer_class = ConfigurationSerializer
    filterset_class = ConfigurationFilter
    # Fields used to search configurations
    search_fields = ['name']
    # Required to remove unneeded ProjectMemberPermission
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

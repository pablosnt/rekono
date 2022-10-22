from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from system.models import System
from system.serializers import SystemSerializer

# Create your views here.


class SystemViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    http_method_names = ['get', 'put']
    # Required to remove unneeded ProjectMemberPermission
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

from rest_framework.permissions import IsAuthenticated

from framework.views import BaseViewSet
from integrations.filters import IntegrationFilter
from integrations.models import Integration
from integrations.serializers import IntegrationSerializer
from security.authorization.permissions import RekonoModelPermission

# Create your views here.


class IntegrationViewSet(BaseViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    filterset_class = IntegrationFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name", "enabled"]
    http_method_names = ["get", "put"]

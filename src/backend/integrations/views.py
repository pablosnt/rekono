from framework.views import BaseViewSet
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import RekonoModelPermission
from integrations.models import Integration
from integrations.serializers import IntegrationSerializer
from integrations.filters import IntegrationFilter

# Create your views here.


class IntegrationViewSet(BaseViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    filterset_class = IntegrationFilter
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = ["get", "put"]

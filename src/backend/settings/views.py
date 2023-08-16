from framework.views import BaseViewSet

# from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from settings.models import Settings
from settings.serializers import SettingsSerializer

# Create your views here.


class SettingsViewSet(BaseViewSet):
    """System ViewSet that includes: retrieve and update features."""

    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    http_method_names = ["get", "put"]  # Required to remove PATCH method
    # Required to remove unneeded ProjectMemberPermission
    # permission_classes = [IsAuthenticated, DjangoModelPermissions]

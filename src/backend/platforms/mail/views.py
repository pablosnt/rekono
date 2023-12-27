from framework.views import BaseViewSet
from platforms.mail.models import SMTPSettings
from platforms.mail.serializers import SMTPSettingsSerializer
from rest_framework.permissions import IsAuthenticated
from security.authorization.permissions import RekonoModelPermission

# Create your views here.


class SMTPSettingsViewSet(BaseViewSet):
    queryset = SMTPSettings.objects.all()
    serializer_class = SMTPSettingsSerializer
    permission_classes = [IsAuthenticated, RekonoModelPermission]
    http_method_names = [
        "get",
        "put",
    ]

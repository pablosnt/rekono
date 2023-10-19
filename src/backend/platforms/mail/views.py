from framework.views import BaseViewSet
from platforms.mail.models import SMTPSettings
from platforms.mail.serializers import SMTPSettingsSerializer

# Create your views here.


class SMTPSettingsViewSet(BaseViewSet):
    queryset = SMTPSettings.objects.all()
    serializer_class = SMTPSettingsSerializer
    http_method_names = [
        "get",
        "put",
    ]

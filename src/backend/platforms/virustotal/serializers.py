from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from platforms.virustotal.integrations import VirusTotal
from platforms.virustotal.models import VirusTotalSettings


class VirusTotalSettingsSerializer(ModelSerializer):
    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)
    client = VirusTotal()

    class Meta:
        model = VirusTotalSettings
        fields = ("id", "api_token", "is_available")

    def get_is_available(self, instance: VirusTotalSettings) -> bool:
        return self.client.is_available()

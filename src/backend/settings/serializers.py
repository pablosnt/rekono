from rest_framework.serializers import ModelSerializer
from settings.models import Settings


class SettingsSerializer(ModelSerializer):
    class Meta:
        model = Settings
        fields = (
            "id",
            "max_uploaded_file_mb",
            "all_proxy",
            "http_proxy",
            "https_proxy",
            "ftp_proxy",
            "no_proxy",
        )

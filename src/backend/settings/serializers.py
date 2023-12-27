from rest_framework.serializers import ModelSerializer
from settings.models import Settings


class SettingsSerializer(ModelSerializer):
    class Meta:
        model = Settings
        fields = (
            "id",
            "max_uploaded_file_mb",
        )

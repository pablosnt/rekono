"""Serializer of the settings endpoints."""

from rest_framework.serializers import ModelSerializer

from settings.models import Settings


class SettingsSerializer(ModelSerializer):
    """Serializer of the Rekono configuration."""

    class Meta:
        """Serializer configuration for the settings."""

        model = Settings
        fields = (
            "id",
            "max_uploaded_file_mb",
            "all_proxy",
            "http_proxy",
            "https_proxy",
            "ftp_proxy",
            "no_proxy",
            "auto_fix_findings",
        )

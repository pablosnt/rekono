"""Settings serializers for Rekono API.

Provides the serializer used to expose and update the global Settings model
through REST API endpoints, covering file upload limits, proxy configuration,
and the auto-fix findings flag.
"""

from rest_framework.serializers import ModelSerializer

from settings.models import Settings


class SettingsSerializer(ModelSerializer):
    """Serializer for Settings model API operations.

    Handles serialization and deserialization of Settings model data,
    exposing file upload limits, proxy configuration, and the auto-fix
    findings flag through the REST API.
    """

    class Meta:
        """Meta configuration for the SettingsSerializer.

        Attributes:
            model (Model): The Settings model to serialize
            fields (tuple): Field names to include in serialization
        """

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

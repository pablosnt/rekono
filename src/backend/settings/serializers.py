"""Settings serializers for Rekono API.

This module provides data serialization and validation for Settings model
through REST API endpoints. It handles secure transformation of configuration
data between internal models and API representations.
"""

from rest_framework.serializers import ModelSerializer

from settings.models import Settings


class SettingsSerializer(ModelSerializer):
    """Serializer for Settings model API operations.

    Handles serialization and deserialization of Settings model data for
    REST API operations. Provides validation and secure data transformation
    for global platform configuration management.
    """
    class Meta:
        """Serializer metadata configuration for Settings model.

        Defines the model binding and field exposure configuration for the
        SettingsSerializer. Specifies which Settings model fields are included
        in API serialization and deserialization operations.

        Attributes:
            model: Settings model class for serializer binding.
            fields: Tuple of field names exposed through the API interface.
                Includes configuration parameters for file uploads, proxy settings,
                and security policy controls.
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

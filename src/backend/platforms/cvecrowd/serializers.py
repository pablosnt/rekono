"""Django REST framework serializers for CVE Crowd platform management.

Serializer classes for converting CVE Crowd settings models to/from JSON
for API operations. Includes secure credential handling, validation logic,
and platform availability detection for threat intelligence integration.
"""

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from platforms.cvecrowd.integrations import CveCrowd
from platforms.cvecrowd.models import CveCrowdSettings
from security.validators.input_validator import Regex, Validator


class CveCrowdSettingsSerializer(ModelSerializer):
    """Serializer for CVE Crowd platform settings.

    Handles serialization and deserialization of CVE Crowd settings with
    secure API token management and platform availability validation.
    Provides protected credential handling and real-time availability status.

    Attributes:
        api_token (ProtectedSecretField): Protected API token field with validation
        is_available (SerializerMethodField): Platform availability status
    """

    api_token = ProtectedSecretField(
        validators=[Validator(Regex.SECRET, code="api_token")], required=False, allow_null=True, source="secret"
    )
    is_available = SerializerMethodField(read_only=True)
    client = CveCrowd()

    class Meta:
        model = CveCrowdSettings
        fields = ("id", "trending_span_days", "execute_per_execution", "api_token", "is_available")

    def get_is_available(self, instance: CveCrowdSettings) -> bool:
        """Check if the CVE Crowd platform is available and accessible.

        Validates platform connectivity and API accessibility using the
        configured credentials and settings.

        Args:
            instance (CveCrowdSettings): The settings instance being serialized.

        Returns:
            bool: True if the platform is available and accessible, False otherwise.
        """
        return self.client.is_available()

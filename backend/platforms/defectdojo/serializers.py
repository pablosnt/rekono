"""Django REST framework serializers for DefectDojo integration management.

Provides serializer classes for DefectDojo configuration, synchronization mappings,
and entity management with secure handling of sensitive data, validation, and
integration with DefectDojo API client for entity existence verification.
"""

from typing import Any

from django.core.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from framework.fields import ProtectedSecretField
from platforms.defectdojo.integrations import DefectDojo
from platforms.defectdojo.models import (
    DefectDojoSettings,
    DefectDojoSync,
    DefectDojoTargetSync,
)


class DefectDojoClientMixin:
    """Mixin providing DefectDojo client access for serializers.

    Provides shared DefectDojo integration client instance for serializers
    that need to interact with DefectDojo API for validation or entity creation.

    Attributes:
        client (DefectDojo): Shared DefectDojo integration client instance
    """

    client = DefectDojo()


class DefectDojoSettingsSerializer(DefectDojoClientMixin, ModelSerializer):
    """Serializer for DefectDojo integration settings with security validation.

    Provides secure serialization of DefectDojo server configuration including
    protected API token field handling and service availability checking.
    Includes input validation, URL normalization, and real-time connectivity testing.

    Attributes:
        api_token (ProtectedSecretField): Secure API token field with validation
        is_available (SerializerMethodField): Real-time DefectDojo service availability
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        """Meta configuration for DefectDojoSettingsSerializer.

        Attributes:
            model (Model): The DefectDojoSettings model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = DefectDojoSettings
        fields = ("id", "server", "api_token", "tls_validation", "tag", "is_available")

    def get_is_available(self, instance: DefectDojoSettings) -> bool:
        """Check if DefectDojo service is currently available and functional.

        Tests DefectDojo connection and configuration to determine if integration
        is properly configured and the service is accessible.

        Args:
            instance (DefectDojoSettings): DefectDojo settings instance to test

        Returns:
            bool: True if DefectDojo service is available and functional, False otherwise
        """
        return self.client.is_available()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize DefectDojo server configuration.

        Performs URL normalization by removing API paths and trailing slashes
        to ensure consistent server URL format for API interactions.

        Args:
            attrs (dict[str, Any]): Serializer attribute dictionary

        Returns:
            dict[str, Any]: Validated and normalized attributes
        """
        attrs = super().validate(attrs)
        if attrs.get("server"):
            if "/api/v2" in attrs["server"]:
                attrs["server"] = attrs["server"].replace("/api/v2", "")
            if attrs["server"][-1] == "/":
                attrs["server"] = attrs["server"][:-1]
        return attrs


class DefectDojoSyncSerializer(DefectDojoClientMixin, ModelSerializer):
    """Serializer for DefectDojo project synchronization mappings.

    Provides serialization for project-level synchronization configurations
    that map Rekono projects to DefectDojo hierarchical entities. Includes
    validation for referenced DefectDojo entities.
    """

    class Meta:
        """Meta configuration for DefectDojoSyncSerializer.

        Attributes:
            model (Model): The DefectDojoSync model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = DefectDojoSync
        fields = ("id", "project", "product_id", "engagement_id", "reimport", "close_old_findings")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate DefectDojo integration availability and entity references.

        Performs comprehensive validation including DefectDojo service availability
        and existence verification for referenced entities (products, engagements)
        to prevent creation of orphaned or invalid relationships.

        Args:
            attrs (dict[str, Any]): Serializer attribute dictionary

        Returns:
            dict[str, Any]: Validated attributes

        Raises:
            ValidationError: If DefectDojo is unavailable or referenced entities don't exist
        """
        if not self.client.is_available():
            raise ValidationError("DefectDojo integration is not configured", code="defectdojo")
        attrs = super().validate(attrs)
        product_id = attrs.get("product_id") or attrs.get("product")
        engagement_id = attrs.get("engagement_id") or attrs.get("engagement")
        product = engagement = None
        if product_id:
            product, exists = self.client.exists("products", product_id)
            if not exists:
                raise ValidationError(f"Product {product_id} doesn't exist", code="product")
        if engagement_id:
            engagement, exists = self.client.exists("engagements", engagement_id)
            if not exists:
                raise ValidationError(f"Engagement {engagement_id} doesn't exist", code="engagement")
            # Verify the engagement belongs to the referenced product
            if product and engagement and engagement.get("product") != product_id:
                raise ValidationError(
                    f"Engagement {engagement_id} doesn't belong to product {product_id}", code="engagement"
                )
        return attrs


class DefectDojoTargetSyncSerializer(DefectDojoClientMixin, ModelSerializer):
    """Serializer for DefectDojo target-specific synchronization mappings.

    Provides serialization for target-level synchronization configurations
    that map individual Rekono targets to specific DefectDojo engagements
    for granular vulnerability tracking and assessment isolation.
    """

    class Meta:
        """Meta configuration for DefectDojoTargetSyncSerializer.

        Attributes:
            model (Model): The DefectDojoTargetSync model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = DefectDojoTargetSync
        fields = ("id", "defectdojo_sync", "target", "engagement_id")

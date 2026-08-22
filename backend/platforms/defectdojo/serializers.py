"""Serializers of the DefectDojo endpoints."""

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
    """Client that the serializers use to ask things to DefectDojo.

    Attributes:
        client: Client shared by all the serializers.
    """

    client = DefectDojo()


class DefectDojoSettingsSerializer(DefectDojoClientMixin, ModelSerializer):
    """Serializer of the DefectDojo configuration.

    Attributes:
        api_token: API token, which is masked when the settings are read.
        is_available: Whether the configured server answers.
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        """Serializer configuration for the DefectDojo settings."""

        model = DefectDojoSettings
        fields = ("id", "server", "api_token", "tls_validation", "tag", "is_available")

    def get_is_available(self, instance: DefectDojoSettings) -> bool:
        """Check if the configured server answers.

        Args:
            instance: Settings being serialized, not read because the check is
              performed against the live platform.

        Returns:
            Whether the platform answers with the configured settings.
        """
        return self.client.is_available()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the configuration and clean the URL of the server.

        Args:
            attrs: Settings values sent by the user, including the server URL.

        Returns:
            The validated data, with the URL of the server as Rekono needs it,
            since the users tend to configure the URL of the API instead.
        """
        attrs = super().validate(attrs)
        if attrs.get("server"):
            if "/api/v2" in attrs["server"]:
                attrs["server"] = attrs["server"].replace("/api/v2", "")
            if attrs["server"][-1] == "/":
                attrs["server"] = attrs["server"][:-1]
        return attrs


class DefectDojoSyncSerializer(DefectDojoClientMixin, ModelSerializer):
    """Serializer of the synchronization between a project and DefectDojo."""

    class Meta:
        """Serializer configuration for the project synchronizations."""

        model = DefectDojoSync
        fields = ("id", "project", "product_id", "engagement_id", "reimport", "close_old_findings")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check that the product and the engagement exist in DefectDojo.

        Args:
            attrs: Synchronization values sent by the user, whose product and
              engagement are looked up in DefectDojo.

        Returns:
            The validated data.

        Raises:
            ValidationError: If DefectDojo can't be used, if the product or the
                engagement don't exist, or if the engagement belongs to another
                product, since the findings would be sent nowhere otherwise.
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
            if product and engagement and engagement.get("product") != product_id:
                raise ValidationError(
                    f"Engagement {engagement_id} doesn't belong to product {product_id}", code="engagement"
                )
        return attrs


class DefectDojoTargetSyncSerializer(DefectDojoClientMixin, ModelSerializer):
    """Serializer of the synchronization between a target and DefectDojo."""

    class Meta:
        """Serializer configuration for the target synchronizations."""

        model = DefectDojoTargetSync
        fields = ("id", "defectdojo_sync", "target", "engagement_id")

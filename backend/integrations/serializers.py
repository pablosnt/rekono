"""Serializer of the integration endpoints."""

from rest_framework.serializers import ModelSerializer

from integrations.models import Integration


class IntegrationSerializer(ModelSerializer):
    """Serializer of an external platform.

    Only the enabled flag can be changed, since the rest of the data comes from
    the fixtures.
    """

    class Meta:
        """Serializer configuration for the integrations."""

        model = Integration
        fields = ("id", "name", "description", "enabled", "reference", "icon")
        read_only_fields = ("id", "name", "description", "reference", "icon")

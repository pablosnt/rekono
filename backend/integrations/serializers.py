"""Serializer of the integration endpoints."""

from rest_framework.serializers import ModelSerializer

from integrations.models import Integration


class IntegrationSerializer(ModelSerializer):
    """Serializer of an external platform.

    Only the enabled flag can be changed, since the rest of the data is created by
    the migrations. The key is exposed because it's what identifies a platform, so
    the clients don't have to rely on the identifier that the database assigned.
    """

    class Meta:
        """Serializer configuration for the integrations."""

        model = Integration
        fields = ("id", "key", "name", "description", "enabled", "reference", "icon")
        read_only_fields = ("id", "key", "name", "description", "reference", "icon")

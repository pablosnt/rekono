"""Serializers for the integrations app.

This module provides Django REST Framework serializers for the Integration
model, enabling API serialization and deserialization of integration data.
"""

from rest_framework.serializers import ModelSerializer

from integrations.models import Integration


class IntegrationSerializer(ModelSerializer):
    """Serializer for the Integration model.

    This serializer handles the conversion of Integration model instances to
    and from JSON format for API communication. It exposes the essential
    fields needed for integration management while protecting certain fields
    from modification.
    """

    class Meta:
        """Meta configuration for the IntegrationSerializer.

        This inner class defines the serializer's configuration, specifying
        which model to serialize, which fields to include, and which fields
        should be read-only.

        Attributes:
            model: The Django model class to serialize (Integration).
            fields: Tuple of field names to include in serialization.
            read_only_fields: Tuple of field names that cannot be modified
                through the API.
        """

        model = Integration
        fields = ("id", "name", "description", "enabled", "reference", "icon")
        read_only_fields = ("id", "name", "description", "reference", "icon")

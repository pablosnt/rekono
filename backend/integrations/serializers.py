"""Django REST framework serializers for integration management.

Serializer classes for converting integration models to/from JSON for API operations.
Includes read-only fields for integration metadata and editable enabled status.
"""

from rest_framework.serializers import ModelSerializer

from integrations.models import Integration


class IntegrationSerializer(ModelSerializer):
    """Serializer for Integration model.

    Handles serialization and deserialization of Integration objects for API operations.
    Most fields are read-only as integrations are typically configured via fixtures.
    """

    class Meta:
        """Meta configuration for the IntegrationSerializer.

        Attributes:
            model (Model): The Integration model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified via API
        """

        model = Integration
        fields = ("id", "name", "description", "enabled", "reference", "icon")
        read_only_fields = ("id", "name", "description", "reference", "icon")

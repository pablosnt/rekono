"""Django REST framework serializers for input parameters.

Serializer classes for converting input parameter models to/from JSON for API operations.
Both serializers inherit deduplication logic from InputParameterSerializer to prevent
parameter redundancy.
"""

from parameters.framework.serializers import InputParameterSerializer
from parameters.models import InputTechnology, InputVulnerability


class InputTechnologySerializer(InputParameterSerializer):
    """Serializer for InputTechnology model.

    Handles serialization and deserialization of technology parameters for API operations
    with automatic deduplication based on name and version fields.
    """

    class Meta:
        """Meta configuration for the InputTechnologySerializer.

        Attributes:
            model (Model): The InputTechnology model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = InputTechnology
        fields = ("id", "name", "version")


class InputVulnerabilitySerializer(InputParameterSerializer):
    """Serializer for InputVulnerability model.

    Handles serialization and deserialization of vulnerability parameters for API operations
    with automatic deduplication based on CVE identifiers.
    """

    class Meta:
        """Meta configuration for the InputVulnerabilitySerializer.

        Attributes:
            model (Model): The InputVulnerability model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = InputVulnerability
        fields = ("id", "cve")

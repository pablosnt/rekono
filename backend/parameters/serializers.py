"""Serializers of the input parameter endpoints."""

from parameters.framework.serializers import InputParameterSerializer
from parameters.models import InputTechnology, InputVulnerability


class InputTechnologySerializer(InputParameterSerializer):
    """Serializer of a technology that the users know that a target runs."""

    class Meta:
        """Serializer configuration for the input technologies."""

        model = InputTechnology
        fields = ("id", "name", "version")


class InputVulnerabilitySerializer(InputParameterSerializer):
    """Serializer of a vulnerability that the users want to check in a target."""

    class Meta:
        """Serializer configuration for the input vulnerabilities."""

        model = InputVulnerability
        fields = ("id", "cve")

from parameters.framework.serializers import InputParameterSerializer
from parameters.models import InputTechnology, InputVulnerability


class InputTechnologySerializer(InputParameterSerializer):
    """Serializer to manage input technologies via API."""

    class Meta:
        model = InputTechnology
        fields = ("id", "name", "version")


class InputVulnerabilitySerializer(InputParameterSerializer):
    """Serializer to manage input vulnerabilities via API."""

    class Meta:
        model = InputVulnerability
        fields = ("id", "cve")

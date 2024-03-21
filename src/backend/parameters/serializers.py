from rest_framework.serializers import ModelSerializer

from parameters.models import InputTechnology, InputVulnerability


class InputTechnologySerializer(ModelSerializer):
    """Serializer to manage input technologies via API."""

    class Meta:
        model = InputTechnology
        fields = ("id", "target", "name", "version")


class InputVulnerabilitySerializer(ModelSerializer):
    """Serializer to manage input vulnerabilities via API."""

    class Meta:
        model = InputVulnerability
        fields = ("id", "target", "cve")

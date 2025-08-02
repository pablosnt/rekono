from parameters.framework.serializers import InputParameterSerializer
from parameters.models import InputTechnology, InputVulnerability


class InputTechnologySerializer(InputParameterSerializer):
    class Meta:
        model = InputTechnology
        fields = ("id", "name", "version")


class InputVulnerabilitySerializer(InputParameterSerializer):
    class Meta:
        model = InputVulnerability
        fields = ("id", "cve")

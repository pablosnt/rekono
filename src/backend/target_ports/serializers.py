from authentications.serializers import AuthenticationSerializer
from rest_framework.serializers import ModelSerializer
from target_ports.models import TargetPort


class TargetPortSerializer(ModelSerializer):
    """Serializer to manage target ports via API."""

    # TODO: Return serializer in READ ops and expect the ID for POST and PUT
    # authentication = AuthenticationSerializer(many=False, required=False)

    class Meta:
        model = TargetPort
        fields = (
            "id",
            "target",
            "port",
            "path",
            "authentication",
        )

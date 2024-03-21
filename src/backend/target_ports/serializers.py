from rest_framework.serializers import ModelSerializer

from authentications.serializers import AuthenticationSerializer
from target_ports.models import TargetPort


class TargetPortSerializer(ModelSerializer):
    """Serializer to manage target ports via API."""

    authentication = AuthenticationSerializer(many=False, read_only=True)

    class Meta:
        model = TargetPort
        fields = (
            "id",
            "target",
            "port",
            "path",
            "authentication",
        )

from typing import Any, Dict

from authentications.serializers import AuthenticationSerializer
from rest_framework.serializers import ModelSerializer
from target_ports.models import TargetPort


class TargetPortSerializer(ModelSerializer):
    """Serializer to manage target ports via API."""

    authentication = AuthenticationSerializer(many=False, read_only=True)

    class Meta:
        model = TargetPort
        fields = (  # Target port fields exposed via API
            "id",
            "target",
            "port",
            "authentication",
        )
        # Read only fields
        read_only_fields = ("authentication",)

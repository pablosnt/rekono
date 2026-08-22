"""Serializers of the target port endpoints."""

from rest_framework.serializers import ModelSerializer

from authentications.serializers import AuthenticationSerializer
from target_ports.models import TargetPort


class TargetPortSerializer(ModelSerializer):
    """Serializer of a target port, including the credential of its service.

    Attributes:
        authentication: Credential that the tools use for this port, with its
          secret masked.
    """

    authentication = AuthenticationSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration for the target ports."""

        model = TargetPort
        fields = ("id", "target", "port", "path", "authentication")

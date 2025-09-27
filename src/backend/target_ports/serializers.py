"""Django REST framework serializers for target port models.

Provides serialization for target port records with nested authentication
data for comprehensive API responses.
"""

from rest_framework.serializers import ModelSerializer

from authentications.serializers import AuthenticationSerializer
from target_ports.models import TargetPort


class TargetPortSerializer(ModelSerializer):
    """Serializer for TargetPort model.

    Handles serialization of target port instances with nested authentication
    data for comprehensive API responses and secure credential management.

    Attributes:
        authentication (AuthenticationSerializer): Nested authentication details
    """

    authentication = AuthenticationSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for the TargetPortSerializer.

        Attributes:
            model (Model): The TargetPort model to serialize
            fields (tuple): Field names to include in serialization
        """

        model = TargetPort
        fields = ("id", "target", "port", "path", "authentication")

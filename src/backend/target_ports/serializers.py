from rest_framework.serializers import ModelSerializer

from authentications.serializers import AuthenticationSerializer
from target_ports.models import TargetPort


class TargetPortSerializer(ModelSerializer):
    authentication = AuthenticationSerializer(many=False, read_only=True)

    class Meta:
        model = TargetPort
        fields = ("id", "target", "port", "path", "authentication")

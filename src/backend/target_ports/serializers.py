from authentications.models import Authentication
from authentications.serializers import AuthenticationSerializer
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from target_ports.models import TargetPort


class TargetPortSerializer(ModelSerializer):
    """Serializer to manage target ports via API."""

    authentication_id = PrimaryKeyRelatedField(
        many=False,
        write_only=True,
        required=False,
        source="authentication",
        queryset=Authentication.objects.all(),
    )
    authentication = AuthenticationSerializer(many=False, read_only=True)

    class Meta:
        model = TargetPort
        fields = (
            "id",
            "target",
            "port",
            "path",
            "authentication_id",
            "authentication",
        )

from framework.fields import ProtectedSecretField
from platforms.cvecrowd.integrations import CVECrowd
from platforms.cvecrowd.models import CVECrowdSettings
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from security.validators.input_validator import Regex, Validator


class CVECrowdSettingsSerializer(ModelSerializer):
    api_token = ProtectedSecretField(
        validators=[Validator(Regex.SECRET.value, code="api_token")],
        required=False,
        allow_null=True,
        source="secret",
    )
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        model = CVECrowdSettings
        fields = (
            "id",
            "trending_span_days",
            "execute_per_execution",
            "api_token",
            "is_available",
        )

    def get_is_available(self, instance: CVECrowdSettings) -> bool:
        return CVECrowd().is_available()

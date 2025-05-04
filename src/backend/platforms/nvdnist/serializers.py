from framework.fields import ProtectedSecretField
from platforms.nvdnist.integrations import NvdNist
from platforms.nvdnist.models import NvdNistSettings
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from security.validators.input_validator import Regex, Validator


class NvdNistSettingsSerializer(ModelSerializer):
    api_token = ProtectedSecretField(
        validators=[Validator(Regex.SECRET.value, code="api_token")],
        required=False,
        allow_null=True,
        source="secret",
    )
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        model = NvdNistSettings
        fields = (
            "id",
            "api_token",
            "is_available",
        )

    def get_is_available(self, instance: NvdNistSettings) -> bool:
        return NvdNist().is_api_token_available()

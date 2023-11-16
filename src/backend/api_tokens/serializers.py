from typing import Any

from api_tokens.models import ApiToken
from rekono.settings import CONFIG
from rest_framework.serializers import ModelSerializer
from security.cryptography.hashing import hash


class ApiTokenSerializer(ModelSerializer):
    class Meta:
        model = ApiToken
        fields = ("id", "name", "expiration")


class CreateApiTokenSerializer(ModelSerializer):
    class Meta:
        model = ApiToken
        fields = ("id", "key", "name", "expiration")
        read_only_fields = ("key",)

    def save(self, **kwargs: Any) -> ApiToken:
        plain_key = ApiToken.generate_key()
        self.validated_data["key"] = hash(f"{plain_key}:{CONFIG.encryption_key}")
        api_token = super().save(**kwargs)
        api_token.key = plain_key
        return api_token

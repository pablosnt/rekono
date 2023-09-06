from typing import Any, Dict

from api_tokens.models import ApiToken
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.serializers import ModelSerializer
from security.utils.cryptography import hash


class ApiTokenSerializer(ModelSerializer):
    class Meta:
        model = ApiToken
        fields = ("id", "name", "expiration")


class CreateApiTokenSerializer(ModelSerializer):
    class Meta:
        model = ApiToken
        fields = ("id", "key", "name", "expiration")
        read_only_fields = ("key",)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        if attrs["expiration"] <= timezone.now():
            raise ValidationError(
                "Expiration must be future",
                code="expiration",
            )
        return attrs

    def save(self, **kwargs: Any) -> ApiToken:
        plain_key = ApiToken.generate_key()
        self.validated_data["key"] = hash(plain_key)
        api_token = super().save(**kwargs)
        api_token.key = plain_key
        return api_token

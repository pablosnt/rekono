from typing import Any, Dict

from django.core.exceptions import PermissionDenied
from http_headers.models import HttpHeader
from rest_framework.serializers import ModelSerializer
from security.authorization.permissions import IsAdmin


class HttpHeaderSerializer(ModelSerializer):
    class Meta:
        model = HttpHeader
        fields = ("id", "target", "user", "key", "value")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        if attrs.get("target"):
            attrs["user"] = None
        if (
            attrs.get("user") is not None
            and attrs.get("user") != self.context.get("request").user
        ) or (
            attrs.get("target") is None
            and attrs.get("user") is None
            and not IsAdmin().has_permission(self.context.get("request"), None)
        ):
            raise PermissionDenied()
        return attrs


class SimpleHttpHeaderSerializer(ModelSerializer):
    class Meta:
        model = HttpHeader
        fields = ("id", "key", "value")

    def update(
        self, instance: HttpHeader, validated_data: Dict[str, Any]
    ) -> HttpHeader:
        if (
            instance.user is not None
            and instance.user != self.context.get("request").user
        ) or (
            instance.user is None
            and instance.target is None
            and not IsAdmin().has_permission(self.context.get("request"), None)
        ):
            raise PermissionDenied()
        return super().update(instance, validated_data)

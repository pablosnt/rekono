"""Serializers of the HTTP header endpoints."""

from typing import Any

from django.core.exceptions import PermissionDenied
from rest_framework.serializers import ModelSerializer

from http_headers.models import HttpHeader
from security.authorization.permissions import IsAdmin


class HttpHeaderSerializer(ModelSerializer):
    """Serializer of an HTTP header, including the scope where it applies."""

    class Meta:
        """Serializer configuration for the HTTP headers."""

        model = HttpHeader
        fields = ("id", "target", "user", "key", "value")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check that the user can create a header in the requested scope.

        Args:
            attrs: Header fields sent by the user, including its scope.

        Returns:
            The validated data, with the user removed if the header belongs to a
            target, since both scopes can't be applied at the same time.

        Raises:
            PermissionDenied: If the header belongs to another user, or if it's a
                global header and the user isn't an admin.
        """
        attrs = super().validate(attrs)
        if attrs.get("target"):
            attrs["user"] = None
        if (attrs.get("user") is not None and attrs.get("user") != self.context.get("request").user) or (
            attrs.get("target") is None
            and attrs.get("user") is None
            and not IsAdmin().has_permission(self.context.get("request"), None)
        ):
            raise PermissionDenied()
        return attrs


class UpdateHttpHeaderSerializer(ModelSerializer):
    """Serializer of the HTTP header data that can be updated.

    The scope of a header is fixed when it's created, so a header can't be moved to
    another target or user without removing it and creating it again.
    """

    class Meta:
        """Serializer configuration for the HTTP header updates."""

        model = HttpHeader
        fields = ("id", "key", "value")

    def update(self, instance: HttpHeader, validated_data: dict[str, Any]) -> HttpHeader:
        """Update the key and the value of a header.

        Args:
            instance: Header being updated, whose scope can't be changed.
            validated_data: New key and value.

        Returns:
            The updated header.

        Raises:
            PermissionDenied: If the header belongs to another user, or if it's a
                global header and the user isn't an admin.
        """
        if (instance.user is not None and instance.user != self.context.get("request").user) or (
            instance.user is None
            and instance.target is None
            and not IsAdmin().has_permission(self.context.get("request"), None)
        ):
            raise PermissionDenied()
        return super().update(instance, validated_data)

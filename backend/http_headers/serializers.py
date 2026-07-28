"""HTTP Headers serializers for REST API data transformation.

Provides serialization and deserialization for HTTP header data
with comprehensive validation and access control enforcement.
"""

from typing import Any

from django.core.exceptions import PermissionDenied
from rest_framework.serializers import ModelSerializer

from http_headers.models import HttpHeader
from security.authorization.permissions import IsAdmin


class HttpHeaderSerializer(ModelSerializer):
    """Full serializer for HTTP header management with validation.

    Provides complete serialization for HTTP headers including all fields,
    with validation logic that enforces access control when a header is
    created.
    """

    class Meta:
        """Meta configuration for HttpHeaderSerializer.

        Defines model reference and field inclusion for complete
        HTTP header serialization with all relevant attributes.

        Attributes:
            model (type): HttpHeader model class
            fields (tuple): All fields included in serialization
        """

        model = HttpHeader
        fields = ("id", "target", "user", "key", "value")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate HTTP header data with access control enforcement.

        Validates header attributes and enforces security policies including
        target precedence over user assignment, user authorization checks,
        and admin permission validation for global headers.

        Args:
            attrs (dict[str, Any]): Header attributes to validate.

        Returns:
            dict[str, Any]: Validated attributes with proper assignments.

        Raises:
            PermissionDenied: If user lacks permission to create the header.
        """
        attrs = super().validate(attrs)
        # A target-specific header has no user, so clear any user assignment once a target is set
        if attrs.get("target"):
            attrs["user"] = None
        # Users may only assign a header to themselves
        # A global header, which has neither target nor user, is restricted to Admin users
        if (attrs.get("user") is not None and attrs.get("user") != self.context.get("request").user) or (
            attrs.get("target") is None
            and attrs.get("user") is None
            and not IsAdmin().has_permission(self.context.get("request"), None)
        ):
            raise PermissionDenied()
        return attrs


class UpdateHttpHeaderSerializer(ModelSerializer):
    """Serializer for updating an existing HTTP header.

    A header's scope, its target or user association, is fixed when the
    header is created and cannot be reassigned through an update, so this
    serializer only exposes the key and value fields. Includes authorization
    checks for update operations.
    """

    class Meta:
        """Meta configuration for UpdateHttpHeaderSerializer.

        Attributes:
            model (type): HttpHeader model class
            fields (tuple): Field names to include in serialization
        """

        model = HttpHeader
        fields = ("id", "key", "value")

    def update(self, instance: HttpHeader, validated_data: dict[str, Any]) -> HttpHeader:
        """Update HTTP header with authorization validation.

        Updates existing HTTP header instance with comprehensive authorization
        checks to ensure users can only modify headers they have permission to access.

        Args:
            instance (HttpHeader): Existing header instance to update.
            validated_data (dict[str, Any]): Validated data for update.

        Returns:
            HttpHeader: Updated header instance.

        Raises:
            PermissionDenied: If user lacks permission to update the header.
        """
        if (instance.user is not None and instance.user != self.context.get("request").user) or (
            instance.user is None
            and instance.target is None
            and not IsAdmin().has_permission(self.context.get("request"), None)
        ):
            raise PermissionDenied()
        return super().update(instance, validated_data)

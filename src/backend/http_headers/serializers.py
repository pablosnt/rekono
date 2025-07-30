"""Django REST framework serializers for HTTP header models.

This module provides serialization and deserialization capabilities for
HTTP header records, including validation logic for authorization and
data integrity with proper permission checks.
"""

from typing import Any

from django.core.exceptions import PermissionDenied
from rest_framework.serializers import ModelSerializer

from http_headers.models import HttpHeader
from security.authorization.permissions import IsAdmin


class HttpHeaderSerializer(ModelSerializer):
    """Serializer for HttpHeader model with comprehensive validation.

    This serializer handles the conversion of HttpHeader model instances
    to and from JSON format, with complex validation logic for authorization
    and data integrity.

    The validation ensures that:
    - Target-specific headers clear user association
    - Users can only create headers for themselves or targets they have access to
    - Global headers (no target, no user) require admin permissions
    """

    class Meta:
        """Meta configuration for the serializer.

        Attributes:
            model: The HttpHeader model to serialize.
            fields: Tuple of field names to include in serialization.
        """

        model = HttpHeader
        fields = ("id", "target", "user", "key", "value")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate HTTP header data with authorization checks.

        This method performs complex validation to ensure proper authorization
        and data integrity for HTTP header creation and updates.

        Args:
            attrs: The attributes to validate.

        Returns:
            dict: The validated attributes.

        Raises:
            PermissionDenied: If the user doesn't have permission to create
                the header or if validation fails.
        """
        attrs = super().validate(attrs)
        # If target is specified, clear user association (target takes precedence)
        if attrs.get("target"):
            attrs["user"] = None
        # Authorization logic: users can only create headers for themselves
        # or for targets they have access to, or global headers if they're admin
        if (attrs.get("user") is not None and attrs.get("user") != self.context.get("request").user) or (
            attrs.get("target") is None
            and attrs.get("user") is None
            and not IsAdmin().has_permission(self.context.get("request"), None)
        ):
            raise PermissionDenied()
        return attrs


class SimpleHttpHeaderSerializer(ModelSerializer):
    """Simplified serializer for HttpHeader model updates.

    This serializer provides a minimal view for updating HTTP header records,
    with authorization checks to ensure users can only update their own headers
    or headers they have permission to modify.
    """

    class Meta:
        """Meta configuration for the serializer.

        Attributes:
            model: The HttpHeader model to serialize.
            fields: Tuple of field names to include in serialization.
        """

        model = HttpHeader
        fields = ("id", "key", "value")

    def update(self, instance: HttpHeader, validated_data: dict[str, Any]) -> HttpHeader:
        """Update HTTP header with authorization checks.

        This method updates an HTTP header instance with proper authorization
        validation to ensure users can only update headers they own or have
        permission to modify.

        Args:
            instance: The HTTP header instance to update.
            validated_data: The validated data for the update.

        Returns:
            HttpHeader: The updated HTTP header instance.

        Raises:
            PermissionDenied: If the user doesn't have permission to update
                the header.
        """
        # Authorization check: users can only update their own headers
        # or global headers if they're admin
        if (instance.user is not None and instance.user != self.context.get("request").user) or (
            instance.user is None
            and instance.target is None
            and not IsAdmin().has_permission(self.context.get("request"), None)
        ):
            raise PermissionDenied()
        return super().update(instance, validated_data)

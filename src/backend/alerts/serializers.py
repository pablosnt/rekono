"""Django REST framework serializers for alert management.

This module contains the serializer classes used for converting alert and
monitoring settings models to/from JSON for API operations.
"""

from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from alerts.enums import AlertMode
from alerts.models import Alert, MonitorSettings
from users.serializers import SimpleUserSerializer


class AlertSerializer(ModelSerializer):
    """Serializer for Alert model.

    Handles serialization and deserialization of Alert objects for API
    operations. Includes computed fields for subscription status and
    owner information.

    Attributes:
        subscribed: Computed field indicating if current user is subscribed
        owner: Serialized user information for the alert owner
    """

    subscribed = SerializerMethodField(read_only=True)
    owner = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        model = Alert
        fields = (
            "id",
            "project",
            "item",
            "mode",
            "value",
            "enabled",
            "owner",
            "subscribed",
            "subscribers",
            "subscribe_all_members",
        )
        read_only_fields = ("id", "subscribed", "enabled", "owner", "subscribers")
        extra_kwargs = {"subscribe_all_members": {"write_only": True}}

    def get_subscribed(self, instance: Any) -> bool:
        """Get whether the current user is subscribed to this alert.

        Args:
            instance: The Alert instance being serialized

        Returns:
            True if the current user is subscribed, False otherwise
        """
        return instance.subscribers.filter(pk=self.context.get("request").user.id).exists()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate the alert data.

        Ensures that filter mode alerts have a value specified.

        Args:
            attrs: The attributes to validate

        Returns:
            The validated attributes

        Raises:
            ValidationError: If filter mode is selected without a value
        """
        attrs = super().validate(attrs)
        if attrs.get("mode") == AlertMode.FILTER and not attrs.get("value"):
            raise ValidationError("Value is required when the alert mode is 'filter'", code="value")
        attrs["enabled"] = True
        return attrs

    @transaction.atomic()
    def create(self, validated_data: dict[str, Any]) -> Alert:
        """Create a new alert instance.

        Creates the alert and handles subscription setup based on the
        subscribe_all_members flag.

        Args:
            validated_data: The validated data for creating the alert

        Returns:
            The created Alert instance
        """
        alert = super().create(validated_data)
        # If subscribe_all_members is set, subscribe all project members to the alert.
        # Otherwise, only subscribe the alert owner.
        if alert.subscribe_all_members:
            alert.subscribers.set(alert.project.members.all())
        else:
            alert.subscribers.add(alert.owner)
        return alert


class EditAlertSerializer(AlertSerializer):
    """Serializer for editing existing alerts.

    A specialized version of AlertSerializer that restricts which fields
    can be modified during updates.
    """

    class Meta:
        model = Alert
        fields = (
            "id",
            "project",
            "item",
            "mode",
            "value",
            "enabled",
            "owner",
            "subscribed",
            "subscribers",
        )
        read_only_fields = (
            "id",
            "project",
            "item",
            "mode",
            "enabled",
            "owner",
            "subscribed",
            "subscribers",
        )


class MonitorSettingsSerializer(ModelSerializer):
    """Serializer for MonitorSettings model.

    Handles serialization and deserialization of MonitorSettings objects
    for API operations.
    """

    class Meta:
        model = MonitorSettings
        fields = ("id", "last_monitor", "hour_span")
        read_only_fields = ("id", "last_monitor")

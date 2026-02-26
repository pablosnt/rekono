"""Django REST framework serializers for alert management.

Serializer classes for converting alert and monitoring settings models
to/from JSON for API operations. Includes validation logic and computed fields.
"""

from typing import Any

from backend.alerts.enums import AlertItem
from django.db import transaction
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from alerts.models import Alert, MonitorSettings
from users.serializers import SimpleUserSerializer


class AlertSerializer(ModelSerializer):
    """Serializer for Alert model.

    Handles serialization and deserialization of Alert objects for API operations.
    Includes computed fields and validation logic for alert creation.

    Attributes:
        subscribed (SerializerMethodField): Whether current user is subscribed
        owner (SimpleUserSerializer): Serialized user information for alert owner
    """

    subscribed = SerializerMethodField(read_only=True)
    owner = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        """Meta configuration for the AlertSerializer.

        Attributes:
            model (Model): The Alert model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified
            extra_kwargs (dict): Additional field configuration
        """

        model = Alert
        fields = (
            "id",
            "project",
            "item",
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
            instance (Alert): The Alert instance being serialized

        Returns:
            bool: True if the current user is subscribed, False otherwise
        """
        return instance.subscribers.filter(pk=self.context.get("request").user.id).exists()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate the alert data.

        Sets the alert as enabled by default.

        Args:
            attrs (dict): The attributes to validate

        Returns:
            dict: The validated attributes
        """
        attrs = super().validate(attrs)
        filter_field = Alert.mapping[attrs["item"]].get("field")
        if not filter_field:
            attrs["value"] = None
        if attrs["item"] == AlertItem.TRENDING_CVE:
            attrs["value"] = str(True).lower()
        attrs["enabled"] = True
        return attrs

    @transaction.atomic()
    def create(self, validated_data: dict[str, Any]) -> Alert:
        """Create a new alert instance.

        Creates the alert and handles subscription setup. If subscribe_all_members
        is True, all project members are subscribed; otherwise only the owner.

        Args:
            validated_data (dict): The validated data for creating the alert

        Returns:
            Alert: The created Alert instance
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

    Specialized version of AlertSerializer that restricts which fields
    can be modified during updates. Only allows value field modifications.
    """

    class Meta:
        """Meta configuration for the EditAlertSerializer.

        Attributes:
            model (Model): The Alert model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified during updates
        """

        model = Alert
        fields = (
            "id",
            "project",
            "item",
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
            "enabled",
            "owner",
            "subscribed",
            "subscribers",
        )


class MonitorSettingsSerializer(ModelSerializer):
    """Serializer for MonitorSettings model.

    Handles serialization and deserialization of MonitorSettings objects
    for API operations. Provides read-only access to monitoring state.
    """

    class Meta:
        """Meta configuration for the MonitorSettingsSerializer.

        Attributes:
            model (Model): The MonitorSettings model to serialize
            fields (tuple): Field names to include in serialization
            read_only_fields (tuple): Fields that cannot be modified
        """

        model = MonitorSettings
        fields = ("id", "last_monitor", "hour_span")
        read_only_fields = ("id", "last_monitor")

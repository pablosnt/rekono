"""Django REST framework serializers for alert management.

Serializer classes for converting alert models to/from JSON for API operations.
Includes validation logic and computed fields.
"""

from typing import Any

from django.db import transaction
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from alerts.enums import AlertItem
from alerts.models import Alert
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
        """Validate and normalize alert data before saving.

        Clears the filter value when the alert item has no matching field in
        Alert.mapping, since it would never be used to filter findings. Trending
        CVE alerts always get their value forced to "True" so the generic
        value-matching logic in Alert.must_be_triggered only fires for findings
        marked as trending. Enabled is forced to True on every call, including
        updates, since EditAlertSerializer reuses this validate() method.

        Args:
            attrs (dict[str, Any]): The attributes to validate

        Returns:
            dict[str, Any]: The validated attributes
        """
        attrs = super().validate(attrs)
        if attrs.get("item"):
            filter_field = Alert.mapping.get(attrs.get("item"), {}).get("field")
            if not filter_field:
                attrs["value"] = None
            if attrs["item"] == AlertItem.TRENDING_CVE:
                attrs["value"] = str(True)
        attrs["enabled"] = True
        return attrs

    @transaction.atomic()
    def create(self, validated_data: dict[str, Any]) -> Alert:
        """Create a new alert instance.

        Creates the alert and handles subscription setup. If subscribe_all_members
        is True, all project members are subscribed; otherwise only the owner.

        Args:
            validated_data (dict[str, Any]): The validated data for creating the alert

        Returns:
            Alert: The created Alert instance
        """
        alert = super().create(validated_data)
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

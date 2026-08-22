"""Serializers of the alert endpoints."""

from typing import Any

from django.db import transaction
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from alerts.enums import AlertItem
from alerts.models import Alert
from users.serializers import SimpleUserSerializer


class AlertSerializer(ModelSerializer):
    """Serializer of an alert and of the users that it notifies.

    Attributes:
        subscribed: Whether the user that makes the request is subscribed.
        owner: User that created the alert.
    """

    subscribed = SerializerMethodField(read_only=True)
    owner = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        """Serializer configuration for the alerts."""

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
        """Check if the user that makes the request is subscribed to the alert.

        Args:
            instance: Alert being serialized.

        Returns:
            Whether the user is one of its subscribers.
        """
        return instance.subscribers.filter(pk=self.context.get("request").user.id).exists()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Check the alert data and complete it with the value that its item needs.

        Args:
            attrs: Alert fields sent by the user.

        Returns:
            The validated data, with the value removed if the item can't be
            filtered by value, and with the alert always enabled, since a new
            alert is never created as disabled.
        """
        attrs = super().validate(attrs)
        if attrs.get("item"):
            filter_field = Alert.mapping.get(attrs.get("item"), {}).get("field")
            if not filter_field:
                attrs["value"] = None
            # The trending CVE alerts are triggered by the trending field of the vulnerability,
            # so its value is the one that a trending vulnerability has
            if attrs["item"] == AlertItem.TRENDING_CVE:
                attrs["value"] = str(True)
        attrs["enabled"] = True
        return attrs

    @transaction.atomic()
    def create(self, validated_data: dict[str, Any]) -> Alert:
        """Create a new alert and subscribe the users that must be notified.

        Args:
            validated_data: Alert fields, plus the owner that the viewset adds.

        Returns:
            The created alert, whose subscribers are all the members of the project
            or only its owner, depending on how the alert was created.
        """
        alert = super().create(validated_data)
        if alert.subscribe_all_members:
            alert.subscribers.set(alert.project.members.all())
        else:
            alert.subscribers.add(alert.owner)
        return alert


class EditAlertSerializer(AlertSerializer):
    """Serializer of the alert data that can be updated.

    Only the value can be changed, since an alert that watches another item is a
    different alert, and the subscriptions are managed by their own endpoint.
    """

    class Meta:
        """Serializer configuration for the alert updates."""

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

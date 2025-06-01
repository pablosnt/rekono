from typing import Any

from alerts.enums import AlertMode
from alerts.models import Alert, MonitorSettings
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from users.serializers import SimpleUserSerializer


class AlertSerializer(ModelSerializer):
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
        return instance.subscribers.filter(pk=self.context.get("request").user.id).exists()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        if attrs.get("mode") == AlertMode.FILTER and not attrs.get("value"):
            raise ValidationError("Value is required when the alert mode is 'filter'", code="value")
        attrs["enabled"] = True
        return attrs

    @transaction.atomic()
    def create(self, validated_data: dict[str, Any]) -> Alert:
        alert = super().create(validated_data)
        if alert.subscribe_all_members:
            alert.subscribers.set(alert.project.members.all())
        else:
            alert.subscribers.add(alert.owner)
        return alert


class EditAlertSerializer(AlertSerializer):
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
    class Meta:
        model = MonitorSettings
        fields = ("id", "last_monitor", "hour_span")
        read_only_fields = ("id", "last_monitor")

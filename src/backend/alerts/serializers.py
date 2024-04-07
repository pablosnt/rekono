from typing import Any, Dict

from alerts.enums import AlertMode
from alerts.models import Alert, MonitorSettings
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from users.serializers import SimpleUserSerializer


class AlertSerializer(ModelSerializer):
    suscribed = SerializerMethodField(read_only=True)
    suscribers = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        model = Alert
        fields = (
            "id",
            "project",
            "item",
            "mode",
            "value",
            "enabled",
            "suscribed",
            "suscribers",
            "suscribe_all_members",
        )
        read_only_fields = ("id", "suscribed", "enabled", "owner", "suscribers")
        extra_kwargs = {"suscribe_all_members": {"write_only": True}}

    def get_suscribed(self, instance: Any) -> bool:
        return instance.suscribers.filter(
            pk=self.context.get("request").user.id
        ).exists()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        if attrs["mode"] == AlertMode.FILTER and not attrs.get("value"):
            raise ValidationError(
                "Value is required when the alert mode is 'filter'", code="value"
            )
        attrs["enabled"] = True
        return attrs

    @transaction.atomic()
    def create(self, validated_data: Dict[str, Any]) -> Alert:
        alert = super().create(validated_data)
        if alert.suscribe_all_members:
            alert.suscribers.set(alert.project.members.all())
        else:
            alert.suscribers.add(alert.owner)
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
            "suscribed",
            "suscribers",
        )
        read_only_fields = (
            "id",
            "project",
            "item",
            "mode",
            "enabled",
            "suscribed",
            "suscribers",
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        return super(ModelSerializer).validate(attrs)


class MonitorSettingsSerializer(ModelSerializer):
    class Meta:
        model = MonitorSettings
        fields = ("id", "last_monitor", "hour_span")
        read_only_fields = ("id", "last_monitor")

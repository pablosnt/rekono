from typing import Any, Dict

from alerts.models import Alert
from django.db import transaction
from rest_framework.serializers import ModelSerializer
from users.serializers import SimpleUserSerializer


class AlertSerializer(ModelSerializer):
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
            "suscribers",
            "suscribe_all_members",
        )
        read_only_fields = ("id", "enabled", "owner", "suscribers")
        extra_kwargs = {"suscribe_all_members": {"write_only": True}}

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)
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


class EditAlertSerializer(ModelSerializer):
    suscribers = SimpleUserSerializer(many=False, read_only=True)

    class Meta:
        model = Alert
        fields = ("id", "project", "item", "mode", "value", "enabled", "suscribers")
        read_only_fields = ("id", "project", "item", "mode", "enabled", "suscribers")

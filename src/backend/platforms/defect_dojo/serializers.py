from typing import Any, Dict

from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from framework.fields import ProtectedSecretField
from platforms.defect_dojo.integrations import DefectDojo
from platforms.defect_dojo.models import (
    DefectDojoSettings,
    DefectDojoSync,
    DefectDojoTargetSync,
)
from projects.models import Project
from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)
from security.input_validator import Regex, Validator


class DefectDojoSettingsSerializer(ModelSerializer):
    api_token = ProtectedSecretField(
        Validator(Regex.SECRET.value, code="api_token").__call__,
        required=False,
        allow_null=True,
        source="secret",
    )
    is_available = SerializerMethodField(method_name="is_available", read_only=True)

    class Meta:
        model = DefectDojoSettings
        fields = (
            "id",
            "server",
            "api_token",
            "tls_validation",
            "tag",
            "product_type",
            "test_type",
            "test",
        )

    def is_available(self, instance: DefectDojoSettings) -> bool:
        return DefectDojo().is_available()


class DefectDojoSyncSerializer(ModelSerializer):
    class Meta:
        model = DefectDojoSync
        fields = (
            "id",
            "project",
            "product_type_id",
            "product_id",
            "engagement_id",
            "engagement_per_target",
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate()
        if not attrs.get("engagement_id") and not attrs.get("engagement_per_target"):
            raise ValidationError("Engagement is required", code="engagement_id")
        return attrs


class DefectDojoTargetSyncSerializer(ModelSerializer):
    class Meta:
        model = DefectDojoTargetSync
        fields = (
            "id",
            "defect_dojo_sync",
            "target",
            "engagement_id",
        )


class BaseDefectDojoSerializer(Serializer):
    client = None

    def _get_client(self) -> DefectDojo:
        if not self.client:
            self.client = DefectDojo()
        return self.client

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if not self._get_client().is_available():
            raise ValidationError(
                "Defect-Dojo integration hasn't been configured properly",
                code="defect-dojo",
            )
        return super().validate(attrs)


class DefectDojoProductTypeSerializer(BaseDefectDojoSerializer):
    name = CharField(
        required=True,
        allow_blank=False,
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name")],
    )
    description = CharField(
        required=True,
        allow_blank=False,
        max_length=500,
        validators=[Validator(Regex.TEXT.value, code="description")],
    )

    def create(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._get_client().create_product_type(
            validated_data["name"], validated_data["description"]
        )


class DefectDojoProductSerializer(BaseDefectDojoSerializer):
    product_type = IntegerField(
        required=True,
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
    )
    name = CharField(
        required=True,
        allow_blank=False,
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name")],
    )
    description = CharField(
        required=True,
        allow_blank=False,
        max_length=500,
        validators=[Validator(Regex.TEXT.value, code="description")],
    )
    project_id = IntegerField(
        required=True, validators=[MinValueValidator(1), MaxValueValidator(999999999)]
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        get_object_or_404(
            Project,
            id=attrs.get("project_id"),
            members=self.context.get("request").user.id,
        )
        return super().validate(attrs)

    def create(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._get_client().create_product(
            validated_data["product_type"],
            validated_data["name"],
            validated_data["description"],
            [self.client.settings.tag] + (validated_data["project"].tags or []),
        )


class DefectDojoEngagementSerializer(BaseDefectDojoSerializer):
    product = IntegerField(
        required=True,
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
    )
    name = CharField(
        required=True,
        allow_blank=False,
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name")],
    )
    description = CharField(
        required=True,
        allow_blank=False,
        max_length=500,
        validators=[Validator(Regex.TEXT.value, code="description")],
    )

    def create(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._get_client().create_engagement(
            validated_data["product"],
            validated_data["name"],
            validated_data["description"],
            [self.client.settings.tag] + (validated_data["project"].tags or []),
        )

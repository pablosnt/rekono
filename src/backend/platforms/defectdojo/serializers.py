from typing import Any, cast

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from framework.fields import ProtectedSecretField
from platforms.defectdojo.integrations import DefectDojo
from platforms.defectdojo.models import (
    DefectDojoSettings,
    DefectDojoSync,
    DefectDojoTargetSync,
)
from projects.models import Project
from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    Serializer,
    SerializerMethodField,
)
from security.validators.input_validator import Regex, Validator


class DefectDojoSettingsSerializer(ModelSerializer):
    api_token = ProtectedSecretField(
        Validator(Regex.SECRET.value, code="api_token").__call__,
        required=False,
        allow_null=True,
        source="secret",
    )
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        model = DefectDojoSettings
        fields = (
            "id",
            "server",
            "api_token",
            "tls_validation",
            "tag",
            "test_type",
            "test",
            "is_available",
        )

    def get_is_available(self, instance: DefectDojoSettings) -> bool:
        return DefectDojo().is_available()


class BaseDefectDojoSerializer(Serializer):
    _client = None

    @property
    def client(self) -> DefectDojo:
        if not self._client:
            self._client = DefectDojo()
        return self._client

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not self.client.is_available():
            raise ValidationError(
                "Defect-Dojo integration is not configured",
                code="defect-dojo",
            )
        attrs = super().validate(attrs)
        for entity in ["product_type", "product", "engagement"]:
            value = attrs.get(f"{entity}_id") or attrs.get(entity)
            if value:
                if not self.client.exists(f"{entity}s", value):
                    raise ValidationError(f"Entity {value} doesn't exist", code=entity)
        return attrs


class DefectDojoSyncSerializer(BaseDefectDojoSerializer, ModelSerializer):
    class Meta:
        model = DefectDojoSync
        fields = (
            "id",
            "project",
            "product_type_id",
            "product_id",
            "engagement_id",
        )


class DefectDojoTargetSyncSerializer(ModelSerializer):
    class Meta:
        model = DefectDojoTargetSync
        fields = (
            "id",
            "defectdojo_sync",
            "target",
            "engagement_id",
        )


class DefectDojoProductTypeSerializer(BaseDefectDojoSerializer):
    id = IntegerField(read_only=True)
    name = CharField(
        required=True,
        allow_blank=False,
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name")],
        write_only=True,
    )
    description = CharField(
        required=True,
        allow_blank=False,
        max_length=500,
        validators=[Validator(Regex.TEXT.value, code="description")],
        write_only=True,
    )

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        return self.client.create_product_type(validated_data["name"], validated_data["description"])


class DefectDojoProductSerializer(BaseDefectDojoSerializer):
    id = IntegerField(read_only=True)
    product_type = IntegerField(
        required=True,
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        write_only=True,
    )
    name = CharField(
        required=True,
        allow_blank=False,
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name")],
        write_only=True,
    )
    description = CharField(
        required=True,
        allow_blank=False,
        max_length=500,
        validators=[Validator(Regex.TEXT.value, code="description")],
        write_only=True,
    )
    # Needed to add project tags to Defect-Dojo product
    project_id = PrimaryKeyRelatedField(
        required=True,
        queryset=Project.objects.all(),
        write_only=True,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        attrs["project"] = get_object_or_404(
            Project,
            id=cast(Project, attrs.get("project_id")).id,
            members=self.context.get("request").user.id,
        )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        return self.client.create_product(
            validated_data["product_type"],
            validated_data["name"],
            validated_data["description"],
            (
                [self.client.settings.tag]
                if self.client.settings.tag
                else [] + list(validated_data["project"].tags.all().values_list("slug", flat=True))
            ),
        )


class DefectDojoEngagementSerializer(BaseDefectDojoSerializer):
    id = IntegerField(read_only=True)
    product = IntegerField(
        required=True,
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        write_only=True,
    )
    name = CharField(
        required=True,
        allow_blank=False,
        max_length=100,
        validators=[Validator(Regex.NAME.value, code="name")],
        write_only=True,
    )
    description = CharField(
        required=True,
        allow_blank=False,
        max_length=500,
        validators=[Validator(Regex.TEXT.value, code="description")],
        write_only=True,
    )

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        return self.client.create_engagement(
            validated_data["product"],
            validated_data["name"],
            validated_data["description"],
            [self.client.settings.tag] if self.client.settings.tag else [],
        )

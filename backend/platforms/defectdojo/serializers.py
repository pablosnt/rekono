"""Django REST framework serializers for DefectDojo integration management.

Provides serializer classes for DefectDojo configuration, synchronization mappings,
and entity management with secure handling of sensitive data, validation, and
integration with DefectDojo API client for entity existence verification.
"""

from typing import Any, cast

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    Serializer,
    SerializerMethodField,
)

from framework.fields import ProtectedSecretField
from platforms.defectdojo.integrations import DefectDojo
from platforms.defectdojo.models import (
    DefectDojoSettings,
    DefectDojoSync,
    DefectDojoTargetSync,
)
from projects.models import Project
from security.validators.input_validator import Regex, Validator


class DefectDojoClientMixin:
    """Mixin providing DefectDojo client access for serializers.

    Provides shared DefectDojo integration client instance for serializers
    that need to interact with DefectDojo API for validation or entity creation.

    Attributes:
        client (DefectDojo): Shared DefectDojo integration client instance
    """

    client = DefectDojo()


class DefectDojoSettingsSerializer(DefectDojoClientMixin, ModelSerializer):
    """Serializer for DefectDojo integration settings with security validation.

    Provides secure serialization of DefectDojo server configuration including
    protected API token field handling and service availability checking.
    Includes input validation, URL normalization, and real-time connectivity testing.

    Attributes:
        api_token (ProtectedSecretField): Secure API token field with validation
        is_available (SerializerMethodField): Real-time DefectDojo service availability
    """

    api_token = ProtectedSecretField(required=False, allow_null=True, source="secret")
    is_available = SerializerMethodField(read_only=True)

    class Meta:
        """Serializer metadata configuration for DefectDojoSettings model.

        Defines the model to serialize and specifies the fields to include
        in the serialized representation for REST API operations.

        Attributes:
            model: DefectDojoSettings model class for serialization
            fields: Tuple of field names to include in serialization
        """

        model = DefectDojoSettings
        fields = ("id", "server", "api_token", "tls_validation", "tag", "test_type", "test", "is_available")

    def get_is_available(self, instance: DefectDojoSettings) -> bool:
        """Check if DefectDojo service is currently available and functional.

        Tests DefectDojo connection and configuration to determine if integration
        is properly configured and the service is accessible.

        Args:
            instance (DefectDojoSettings): DefectDojo settings instance to test

        Returns:
            bool: True if DefectDojo service is available and functional, False otherwise
        """
        return self.client.is_available()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize DefectDojo server configuration.

        Performs URL normalization by removing API paths and trailing slashes
        to ensure consistent server URL format for API interactions.

        Args:
            attrs (dict[str, Any]): Serializer attribute dictionary

        Returns:
            dict[str, Any]: Validated and normalized attributes
        """
        attrs = super().validate(attrs)
        if attrs.get("server"):
            if "/api/v2" in attrs["server"]:
                attrs["server"] = attrs["server"].replace("/api/v2", "")
            if attrs["server"][-1] == "/":
                attrs["server"] = attrs["server"][:-1]
        return attrs


class BaseDefectDojoSerializer(DefectDojoClientMixin, Serializer):
    """Base serializer for DefectDojo entity operations with validation.

    Provides common validation logic for DefectDojo entity serializers including
    integration availability checking and entity existence verification.
    Ensures all operations are performed against properly configured DefectDojo instances.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate DefectDojo integration availability and entity references.

        Performs comprehensive validation including DefectDojo service availability
        and existence verification for referenced entities (product types, products,
        engagements) to prevent creation of orphaned or invalid relationships.

        Args:
            attrs (dict[str, Any]): Serializer attribute dictionary

        Returns:
            dict[str, Any]: Validated attributes

        Raises:
            ValidationError: If DefectDojo is unavailable or referenced entities don't exist
        """
        if not self.client.is_available():
            raise ValidationError("DefectDojo integration is not configured", code="defectdojo")
        attrs = super().validate(attrs)
        for entity in ["product_type", "product", "engagement"]:
            value = attrs.get(f"{entity}_id") or attrs.get(entity)
            if value:
                if not self.client.exists(f"{entity}s", value):
                    raise ValidationError(f"{entity.capitalize().replace('_', '')} {value} doesn't exist", code=entity)
        return attrs


class DefectDojoSyncSerializer(BaseDefectDojoSerializer, ModelSerializer):
    """Serializer for DefectDojo project synchronization mappings.

    Provides serialization for project-level synchronization configurations
    that map Rekono projects to DefectDojo hierarchical entities. Includes
    validation for referenced DefectDojo entities.
    """

    class Meta:
        """Serializer metadata configuration for DefectDojoSync model.

        Defines the model to serialize and specifies the fields to include
        in the serialized representation for synchronization management.

        Attributes:
            model: DefectDojoSync model class for serialization
            fields: Tuple of field names to include in serialization
        """

        model = DefectDojoSync
        fields = ("id", "project", "product_type_id", "product_id", "engagement_id")


class DefectDojoTargetSyncSerializer(ModelSerializer):
    """Serializer for DefectDojo target-specific synchronization mappings.

    Provides serialization for target-level synchronization configurations
    that map individual Rekono targets to specific DefectDojo engagements
    for granular vulnerability tracking and assessment isolation.
    """

    class Meta:
        """Serializer metadata configuration for DefectDojoTargetSync model.

        Defines the model to serialize and specifies the fields to include
        in the serialized representation for target synchronization management.

        Attributes:
            model: DefectDojoTargetSync model class for serialization
            fields: Tuple of field names to include in serialization
        """

        model = DefectDojoTargetSync
        fields = ("id", "defectdojo_sync", "target", "engagement_id")


class DefectDojoProductTypeSerializer(BaseDefectDojoSerializer):
    """Serializer for creating DefectDojo product types.

    Provides serialization and validation for creating product type entities
    in DefectDojo through direct API integration. Product types serve as the
    top-level organizational structure in DefectDojo's hierarchy.

    Attributes:
        id (IntegerField): Created product type ID (read-only)
        name (CharField): Product type name (write-only, max 100 chars)
        description (CharField): Product type description (write-only, max 500 chars)
        client (DefectDojo): DefectDojo integration client instance inherited from mixin
    """

    id = IntegerField(read_only=True)
    name = CharField(
        required=True,
        allow_blank=False,
        max_length=100,
        validators=[Validator(Regex.NAME, code="name")],
        write_only=True,
    )
    description = CharField(
        required=True,
        allow_blank=False,
        max_length=500,
        validators=[Validator(Regex.TEXT, code="description")],
        write_only=True,
    )

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new product type in DefectDojo.

        Creates a product type entity through DefectDojo API integration
        using validated name and description data.

        Args:
            validated_data (dict[str, Any]): Validated serializer data

        Returns:
            dict[str, Any]: Created product type data from DefectDojo API
        """
        return self.client.create_product_type(validated_data["name"], validated_data["description"])


class DefectDojoProductSerializer(BaseDefectDojoSerializer):
    """Serializer for creating DefectDojo products.

    Provides serialization and validation for creating product entities in DefectDojo
    through direct API integration. Products represent specific applications or
    systems being tested and are associated with product types.

    Attributes:
        id (IntegerField): Created product ID (read-only)
        product_type (IntegerField): DefectDojo product type ID (write-only, 1-999999999)
        name (CharField): Product name (write-only, max 100 chars)
        description (CharField): Product description (write-only, max 500 chars)
        project_id (PrimaryKeyRelatedField): Rekono project ID for tag integration (write-only)
        client (DefectDojo): DefectDojo integration client instance inherited from mixin
    """

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
        validators=[Validator(Regex.NAME, code="name")],
        write_only=True,
    )
    description = CharField(
        required=True,
        allow_blank=False,
        max_length=500,
        validators=[Validator(Regex.TEXT, code="description")],
        write_only=True,
    )
    # Needed to add project tags to DefectDojo product
    project_id = PrimaryKeyRelatedField(
        required=True,
        queryset=Project.objects.all(),
        write_only=True,
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate product creation data and verify project access permissions.

        Validates DefectDojo integration and entity references, then verifies
        that the requesting user has access to the specified project for
        tag integration purposes.

        Args:
            attrs (dict[str, Any]): Serializer attribute dictionary

        Returns:
            dict[str, Any]: Validated attributes with project instance
        """
        attrs = super().validate(attrs)
        attrs["project"] = get_object_or_404(
            Project, id=cast(Project, attrs.get("project_id")).id, members=self.context.get("request").user.id
        )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new product in DefectDojo with project tag integration.

        Creates a product entity through DefectDojo API integration using
        validated data and includes project tags for organizational consistency.

        Args:
            validated_data (dict[str, Any]): Validated serializer data

        Returns:
            dict[str, Any]: Created product data from DefectDojo API
        """
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
    """Serializer for creating DefectDojo engagements.

    Provides serialization and validation for creating engagement entities in
    DefectDojo through direct API integration. Engagements represent specific
    security assessments or testing periods within a product.

    Attributes:
        id (IntegerField): Created engagement ID (read-only)
        product (IntegerField): DefectDojo product ID (write-only, 1-999999999)
        name (CharField): Engagement name (write-only, max 100 chars)
        description (CharField): Engagement description (write-only, max 500 chars)
        client (DefectDojo): DefectDojo integration client instance inherited from mixin
    """

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
        validators=[Validator(Regex.NAME, code="name")],
        write_only=True,
    )
    description = CharField(
        required=True,
        allow_blank=False,
        max_length=500,
        validators=[Validator(Regex.TEXT, code="description")],
        write_only=True,
    )

    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new engagement in DefectDojo with tag integration.

        Creates an engagement entity through DefectDojo API integration using
        validated data and includes configured tags for organizational consistency.

        Args:
            validated_data (dict[str, Any]): Validated serializer data

        Returns:
            dict[str, Any]: Created engagement data from DefectDojo API
        """
        return self.client.create_engagement(
            validated_data["product"],
            validated_data["name"],
            validated_data["description"],
            [self.client.settings.tag] if self.client.settings.tag else [],
        )

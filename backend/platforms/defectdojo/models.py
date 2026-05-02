"""Django models for DefectDojo integration configuration and synchronization.

Provides data models for managing DefectDojo integration settings, project
synchronization mappings, and target-specific engagement tracking. Includes
encrypted credential storage and comprehensive validation for secure integration.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from framework.models import BaseEncrypted, BaseModel
from projects.models import Project
from security.validators.input_validator import Regex, Validator
from targets.models import Target


class DefectDojoSettings(BaseEncrypted):
    """Model representing DefectDojo integration configuration settings.

    Stores DefectDojo server connection parameters, API credentials, and integration
    preferences with automatic encryption of sensitive data. Supports TLS validation,
    custom tagging, and date format configuration for seamless integration.

    Attributes:
        server (TextField): DefectDojo server URL (max 100 chars)
        _api_token (TextField): Encrypted DefectDojo API token (max 40 chars)
        tls_validation (BooleanField): Enable TLS certificate validation (default True)
        tag (TextField): Custom tag for DefectDojo entities (optional, max 200 chars)
        test_type_id (IntegerField): Cached test type ID to avoid duplicates (1-999999999)
        test_type (TextField): Test type name for DefectDojo tests (max 200 chars)
        test (TextField): Test name for DefectDojo tests (max 200 chars)
        date_format (TextField): Date format string for DefectDojo API (max 15 chars)
        datetime_format (TextField): DateTime format string for DefectDojo API (max 15 chars)

    Example:
        Configure DefectDojo integration:

        ```python
        defectdojo_config = DefectDojoSettings.objects.create(
            server="https://defectdojo.company.com",
            secret="your_api_token_here",
            tls_validation=True,
            tag="rekono",
            test_type="Rekono Security Test",
            test="Rekono Assessment",
            date_format="%Y-%m-%d",
            datetime_format="%Y-%m-%d %H:%M:%S"
        )
        ```
    """

    server = models.TextField(max_length=100, validators=[Validator(Regex.TARGET)], blank=True, null=True)
    _api_token = models.TextField(
        max_length=40,
        validators=[Validator(Regex.SECRET, code="api_token")],
        null=True,
        blank=True,
        db_column="api_token",
    )
    tls_validation = models.BooleanField(default=True)
    tag = models.TextField(max_length=200, validators=[Validator(Regex.NAME, code="tag")], blank=True, null=True)
    # Stores Test Type ID to avoid duplicated creation
    test_type_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        blank=True,
        null=True,
    )
    test_type = models.TextField(max_length=200, validators=[Validator(Regex.NAME, code="test_type")])
    test = models.TextField(max_length=200, validators=[Validator(Regex.NAME, code="test")])
    date_format = models.TextField(max_length=15)
    datetime_format = models.TextField(max_length=15)

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        """Return string representation of DefectDojo settings.

        Returns:
            str: DefectDojo server URL or parent string representation if not configured
        """
        return self.server if self.server else super().__str__()


class DefectDojoSync(BaseModel):
    """Model representing project-level synchronization mapping to DefectDojo.

    Maps Rekono projects to DefectDojo hierarchical structure including product types,
    products, and engagements. Enables project-level vulnerability management and
    centralized tracking of security findings across multiple targets.

    DefectDojo Hierarchy:
        Product Type → Product → Engagement → Tests → Findings

    Attributes:
        project (OneToOneField): Associated Rekono project (one-to-one relationship)
        product_id (IntegerField): DefectDojo product ID (optional, 1-999999999)
        engagement_id (IntegerField): DefectDojo engagement ID (optional, 1-999999999)
        reimport (BooleanField): Reimport findings instead of creating new tests (default False)
        close_old_findings (BooleanField): Close old findings not present in new import (default False)

    Example:
        Create project synchronization mapping:

        ```python
        sync = DefectDojoSync.objects.create(
            project=rekono_project,
            product_id=12,
            engagement_id=34,
            reimport=True,
            close_old_findings=False
        )
        ```
    """

    project = models.OneToOneField(Project, related_name="defectdojo_sync", on_delete=models.CASCADE)
    product_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        blank=True,
        null=True,
    )
    engagement_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        blank=True,
        null=True,
    )
    reimport = models.BooleanField(default=False)
    close_old_findings = models.BooleanField(default=False)

    _project_field = "project"

    def __str__(self) -> str:
        """Return string representation of DefectDojo project synchronization.

        Returns:
            str: Formatted string with project name and DefectDojo entity IDs
        """
        return " - ".join([value.__str__() for value in [self.project, self.product_id, self.engagement_id] if value])


class DefectDojoTargetSync(BaseModel):
    """Model representing target-specific synchronization mapping to DefectDojo engagements.

    Maps individual Rekono targets to specific DefectDojo engagements for granular
    vulnerability tracking and assessment isolation. Enables target-level security
    findings organization within the broader project context.

    Attributes:
        defectdojo_sync (ForeignKey): Parent project synchronization mapping
        target (OneToOneField): Associated Rekono target (one-to-one relationship)
        engagement_id (IntegerField): DefectDojo engagement ID for this target (1-999999999)

    Example:
        Create target-specific synchronization:

        ```python
        target_sync = DefectDojoTargetSync.objects.create(
            defectdojo_sync=project_sync,
            target=rekono_target,
            engagement_id=56
        )
        ```
    """

    defectdojo_sync = models.ForeignKey(DefectDojoSync, related_name="target_syncs", on_delete=models.CASCADE)
    target = models.OneToOneField(Target, related_name="defectdojo_sync", on_delete=models.CASCADE)
    engagement_id = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(999999999)])

    _project_field = "defectdojo_sync__project"

    def __str__(self) -> str:
        """Return string representation of DefectDojo target synchronization.

        Returns:
            str: Formatted string with project sync info, target name, and engagement ID
        """
        return " - ".join([self.defectdojo_sync.__str__(), self.target.target, str(self.engagement_id)])

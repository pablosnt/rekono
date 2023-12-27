from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from framework.models import BaseEncrypted, BaseModel
from projects.models import Project
from security.input_validator import Regex, Validator
from targets.models import Target

# Create your models here.


class DefectDojoSettings(BaseEncrypted):
    server = models.TextField(
        max_length=100,
        validators=[Validator(Regex.TARGET.value)],
        blank=True,
        null=True,
    )
    _api_token = models.TextField(
        max_length=40,
        validators=[Validator(Regex.SECRET.value, code="api_token")],
        null=True,
        blank=True,
        db_column="api_token",
    )
    tls_validation = models.BooleanField(default=True)
    tag = models.TextField(
        max_length=200, validators=[Validator(Regex.NAME.value, code="tag")]
    )
    # Stores Test Type ID to avoid duplicated creation
    test_type_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        blank=True,
        null=True,
    )
    test_type = models.TextField(
        max_length=200, validators=[Validator(Regex.NAME.value, code="test_type")]
    )
    test = models.TextField(
        max_length=200, validators=[Validator(Regex.NAME.value, code="test")]
    )
    date_format = models.TextField(max_length=15)
    datetime_format = models.TextField(max_length=15)

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        return self.server if self.server else super().__str__()


class DefectDojoSync(BaseModel):
    project = models.OneToOneField(
        Project, related_name="defect_dojo_sync", on_delete=models.CASCADE
    )
    product_type_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
    )
    product_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
    )
    engagement_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.project.__str__()} - {self.product_type_id} - {self.product_id}{f' - {self.engagement_id}' if self.engagement_id else ''}"

    @classmethod
    def get_project_field(cls) -> str:
        return "project"


class DefectDojoTargetSync(BaseModel):
    defect_dojo_sync = models.ForeignKey(
        DefectDojoSync, related_name="target_syncs", on_delete=models.CASCADE
    )
    target = models.OneToOneField(
        Target, related_name="defect_dojo_sync", on_delete=models.CASCADE
    )
    engagement_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)]
    )

    def __str__(self) -> str:
        return f"{self.defect_dojo_sync.__str__()} - {self.target.target} - {self.engagement_id}"

    @classmethod
    def get_project_field(cls) -> str:
        return "defect_dojo_sync__project"  # pragma: no cover

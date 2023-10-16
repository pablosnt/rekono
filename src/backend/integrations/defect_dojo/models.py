from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from framework.models import BaseModel
from projects.models import Project
from security.utils.input_validator import Regex, Validator
from targets.models import Target

# Create your models here.


class DefectDojoSettings(BaseModel):
    server = models.TextField(
        max_length=100,
        validators=[Validator(Regex.TARGET.value)],
        blank=True,
        null=True,
    )
    # TODO: encrypt and decrypt secret for more security
    api_token = models.TextField(
        max_length=40,
        validators=[Validator(Regex.SECRET.value, code="api_token")],
        null=True,
        blank=True,
    )
    tls_validation = models.BooleanField(default=True)
    tag = models.TextField(
        max_length=200, validators=[Validator(Regex.NAME.value, code="tag")]
    )
    product_type_id = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999999)],
        blank=True,
        null=True,
    )
    product_type = models.TextField(
        max_length=200, validators=[Validator(Regex.NAME.value, code="product_type")]
    )
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
    engagement_per_target = models.BooleanField(default=False)

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

    @classmethod
    def get_project_field(cls) -> str:
        return "defect_dojo_sync__project"

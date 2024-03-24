from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from framework.models import BaseModel
from security.validators.input_validator import Regex, Validator

# Create your models here.


class Settings(BaseModel):
    # Max size in MB for uploaded files
    max_uploaded_file_mb = models.IntegerField(
        default=512, validators=[MinValueValidator(128), MaxValueValidator(3072)]
    )
    all_proxy = models.TextField(
        max_length=300,
        validators=[Validator(Regex.TARGET_REGEX.value)],
        blank=True,
        null=True,
    )
    http_proxy = models.TextField(
        max_length=300,
        validators=[Validator(Regex.TARGET_REGEX.value)],
        blank=True,
        null=True,
    )
    https_proxy = models.TextField(
        max_length=300,
        validators=[Validator(Regex.TARGET_REGEX.value)],
        blank=True,
        null=True,
    )
    ftp_proxy = models.TextField(
        max_length=300,
        validators=[Validator(Regex.TARGET_REGEX.value)],
        blank=True,
        null=True,
    )
    no_proxy = models.TextField(
        max_length=300,
        validators=[Validator(Regex.TARGET_REGEX.value)],
        blank=True,
        null=True,
    )
    auto_fix_findings = models.BooleanField(default=True)

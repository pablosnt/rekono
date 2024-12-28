from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from framework.models import BaseEncrypted
from security.validators.input_validator import Regex, Validator

# Create your models here.


# TODO: Don't split defect_dojo word
# TODO: Don't use uppercase in CVECrowd


class NvdNistSettings(BaseEncrypted):
    _api_token = models.TextField(
        max_length=50,
        validators=[Validator(Regex.SECRET.value, code="api_token")],
        null=True,
        blank=True,
        db_column="api_token",
    )

    _encrypted_field = "_api_token"

    def __str__(self) -> str:
        return "NVD NIST"

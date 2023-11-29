from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from framework.models import BaseModel

# Create your models here.


class Settings(BaseModel):
    # Max size in MB for uploaded files
    max_uploaded_file_mb = models.IntegerField(
        default=512, validators=[MinValueValidator(128), MaxValueValidator(3072)]
    )

    def __str__(self) -> str:
        """Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        """
        return self.__class__.__name__

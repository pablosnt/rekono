from django.db import models
from framework.models import BaseModel

# Create your models here.


class Integration(BaseModel):
    key = models.TextField(max_length=100)
    name = models.TextField(max_length=100)
    description = models.TextField(max_length=500)
    enabled = models.BooleanField(default=True)
    reference = models.TextField(max_length=250)
    icon = models.TextField(max_length=250, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

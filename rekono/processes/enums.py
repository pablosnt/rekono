from django.db import models


class StepPriority(models.TextChoices):
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'

from django.db import models


class Severity(models.IntegerChoices):
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5
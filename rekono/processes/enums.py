from django.db import models


class StepPriority(models.IntegerChoices):
    ASAP = 1
    STANDARD = 2
    LAST = 3

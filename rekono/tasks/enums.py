from django.db import models

# Create your enums here.


class Status(models.IntegerChoices):
    REQUESTED = 1
    SKIPPED = 2
    RUNNING = 3
    CANCELLED = 4
    ERROR = 5
    COMPLETED = 6


class ParameterKey(models.IntegerChoices):
    TECHNOLOGY = 1
    VERSION = 2
    HTTP_ENDPOINT = 3
    CVE = 4
    EXPLOIT = 5
    WORDLIST = 6


class TimeUnit(models.IntegerChoices):
    MINUTES = 1
    HOURS = 2
    DAYS = 3
    WEEKS = 4

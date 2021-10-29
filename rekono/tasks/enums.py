from django.db import models

# Create your enums here.


class Status(models.TextChoices):
    REQUESTED = 'Requested'
    SKIPPED = 'Skipped'
    RUNNING = 'Running'
    CANCELLED = 'Cancelled'
    ERROR = 'Error'
    COMPLETED = 'Completed'


class ParameterKey(models.TextChoices):
    TECHNOLOGY = 'Technology'
    VERSION = 'Version'
    ENDPOINT = 'Endpoint'
    CVE = 'CVE'
    EXPLOIT = 'Exploit'
    WORDLIST = 'Wordlist'


class TimeUnit(models.TextChoices):
    MINUTES = 'Minutes'
    HOURS = 'Hours'
    DAYS = 'Days'
    WEEKS = 'Weeks'

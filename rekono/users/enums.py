from django.db import models


class Notification(models.TextChoices):
    DISABLED = 'Disabled'
    OWN_EXECUTIONS = 'Only my executions'
    ALL_EXECUTIONS = 'All executions'

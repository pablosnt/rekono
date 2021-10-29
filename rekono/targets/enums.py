from django.db import models


class TargetType(models.TextChoices):
    PRIVATE_IP = 'Private IP'
    PUBLIC_IP = 'Public IP'
    NETWORK = 'Network'
    IP_RANGE = 'IP range'
    DOMAIN = 'Domain'

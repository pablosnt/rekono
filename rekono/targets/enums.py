from django.db import models


class TargetType(models.TextChoices):
    '''Supported target types.'''

    PRIVATE_IP = 'Private IP'
    PUBLIC_IP = 'Public IP'
    NETWORK = 'Network'
    IP_RANGE = 'IP range'
    DOMAIN = 'Domain'


class TargetAuthenticationType(models.TextChoices):
    '''Supported target authentication types.'''

    BASIC = 'Basic'
    BEARER = 'Bearer'
    COOKIE = 'Cookie'
    DIGEST = 'Digest'
    JWT = 'JWT'
    NTLM = 'NTLM'

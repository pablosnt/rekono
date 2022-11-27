from django.db import models


class TargetType(models.TextChoices):
    '''Supported target types.'''

    PRIVATE_IP = 'Private IP'
    PUBLIC_IP = 'Public IP'
    NETWORK = 'Network'
    IP_RANGE = 'IP range'
    DOMAIN = 'Domain'


class TargetCredentialType(models.TextChoices):
    '''Supported target credential types.'''

    COOKIE = 'Cookie'
    DIGEST = 'Digest'
    BEARER = 'Bearer'
    NTLM = 'NTLM'
    JWT = 'JWT'
    OAUTH2 = 'OAuth2'
    PASSWORD = 'Password'

from django.db import models


class WordlistType(models.TextChoices):
    '''Wordlist type names.'''

    ENDPOINT = 'Endpoint'
    SUBDOMAIN = 'Subdomain'

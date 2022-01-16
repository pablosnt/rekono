from django.db import models


class WordlistType(models.TextChoices):
    '''Wordlist type names.'''

    PASSWORD = 'Password'
    ENDPOINT = 'Endpoint'

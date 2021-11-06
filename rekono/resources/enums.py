from django.db import models


class WordlistType(models.TextChoices):
    PASSWORD = 'Password'
    ENDPOINT = 'Endpoint'

from django.db import models
from resources.enums import WordlistType

# Create your models here.


class Wordlist(models.Model):
    name = models.TextField(max_length=50, unique=True)
    type = models.TextField(max_length=10, choices=WordlistType.choices)
    path = models.TextField(max_length=100, unique=True)

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name

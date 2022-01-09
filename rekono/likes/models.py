from django.conf import settings
from django.db import models

# Create your models here.


class LikeBase(models.Model):
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_%(class)s')

    class Meta:
        abstract = True

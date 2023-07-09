from django.conf import settings
from django.db import models

# Create your models here.


class LikeBase(models.Model):
    '''Common and abstract LikeBase model, to define common fields for all models that user can like.'''

    # Relation with all users that likes each entity
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_%(class)s')

    class Meta:
        '''Model metadata.'''

        # To be extended by models that can be liked
        abstract = True

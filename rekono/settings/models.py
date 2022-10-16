from django.conf import settings
from django.db import models

# Create your models here.

class Setting(models.Model):

    # Problems:
    #   Validate values using reference to validation method or create specific validation method for each one
    #   Implement validation of Defect-Dojo configuration: new unchanged row or specific api request

    field = models.TextField(max_length=30, unique=True)
    # Encrypt value if protected or always if it's not possible
    value = models.TextField(max_length=100, blank=True, null=True)
    protected = models.BooleanField(default=False)
    # Apply validation dinamically
    # validator = models.TextField(max_length=30)
    last_modified = models.DateTimeField(blank=True, null=True)
    # TODO: auto updated when modified
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.field

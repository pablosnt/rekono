from django.conf import settings
from django.db import models

# Create your models here.

class Setting(models.Model):
    field = models.TextField(max_length=30, unique=True)
    # This should be encrypted to protect Telegram token and Defect-Dojo API key, but there isn't a good way to do that
    value = models.TextField(max_length=100, blank=True, null=True)
    private = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        '''Instance representation in text format.

        Returns:
            str: String value that identifies this instance
        '''
        return self.field

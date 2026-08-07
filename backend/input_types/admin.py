"""Registration of the input type model in the Django admin site."""

from django.contrib import admin

from input_types.models import InputType

admin.site.register(InputType)

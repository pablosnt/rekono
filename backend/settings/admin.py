"""Registration of the settings model in the Django admin site."""

from django.contrib import admin

from settings.models import Settings

admin.site.register(Settings)

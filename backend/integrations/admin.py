"""Registration of the integration model in the Django admin site."""

from django.contrib import admin

from integrations.models import Integration

admin.site.register(Integration)

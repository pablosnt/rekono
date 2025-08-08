"""Django admin configuration for integrations module.

Registers Integration model with Django admin interface for
administrative management of third-party integrations.
"""

from django.contrib import admin

from integrations.models import Integration

admin.site.register(Integration)

"""Django admin configuration for settings module.

Registers the Settings model with the Django admin interface for
administrative access to global platform configuration parameters.
"""

from django.contrib import admin

from settings.models import Settings

admin.site.register(Settings)

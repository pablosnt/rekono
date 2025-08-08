"""Settings Django admin configuration.

This module registers the Settings model with Django admin interface for
administrative access to global platform configuration parameters.
"""

from django.contrib import admin

from settings.models import Settings

admin.site.register(Settings)

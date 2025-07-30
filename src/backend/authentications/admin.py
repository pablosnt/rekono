"""Django admin configuration for authentication models.

This module configures the Django admin interface for authentication-related
models, allowing administrators to manage authentication records through
the Django admin panel.
"""

from django.contrib import admin

from authentications.models import Authentication

admin.site.register(Authentication)

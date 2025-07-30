"""Django admin configuration for HTTP header models.

This module configures the Django admin interface for HTTP header-related
models, allowing administrators to manage HTTP header records through
the Django admin panel.
"""

from django.contrib import admin

from http_headers.models import HttpHeader

admin.site.register(HttpHeader)

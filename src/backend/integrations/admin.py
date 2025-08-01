"""Django admin configuration for the integrations app.

This module configures the Django admin interface for the Integration model,
providing a web-based interface for managing integration configurations.
"""

from django.contrib import admin

from integrations.models import Integration

admin.register(Integration)

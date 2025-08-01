"""Django admin configuration for the input_types app.

This module configures the Django admin interface for the InputType model,
providing a web-based interface for managing input type definitions.
"""

from django.contrib import admin

from input_types.models import InputType

admin.register(InputType)

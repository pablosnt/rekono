"""Django admin configuration for execution models.

This module configures the Django admin interface for execution-related
models, allowing administrators to monitor and manage execution records
through the Django admin panel.
"""

from django.contrib import admin

from executions.models import Execution

admin.site.register(Execution)

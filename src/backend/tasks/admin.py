"""Django admin configuration for task models.

Registers task models with the Django admin interface for
administrative management and monitoring.
"""

from django.contrib import admin

from tasks.models import Task

admin.site.register(Task)

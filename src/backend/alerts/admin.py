"""Django admin configuration for alerts module.

Registers the Alert model with Django admin interface for administrative
management of alert configurations. Provides basic CRUD operations for alerts.
"""

from django.contrib import admin

from alerts.models import Alert

admin.site.register(Alert)

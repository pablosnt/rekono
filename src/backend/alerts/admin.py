"""Django admin configuration for alerts module.

This module registers the Alert model with the Django admin interface
for administrative management of alert configurations.
"""

from django.contrib import admin

from alerts.models import Alert

admin.site.register(Alert)

"""Django admin configuration for monitor module.

Registers the MonitorSettings model with Django admin interface for
administrative management of monitoring configuration.
"""

from django.contrib import admin

from monitor.models import MonitorSettings

admin.site.register(MonitorSettings)

"""Registration of the monitor settings model in the Django admin site."""

from django.contrib import admin

from monitor.models import MonitorSettings

admin.site.register(MonitorSettings)

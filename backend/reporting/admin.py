"""Django admin configuration for reporting models.

Registers the Report model with the Django admin interface for
administrative management and monitoring of report generation records.
"""

from django.contrib import admin

from reporting.models import Report

admin.site.register(Report)

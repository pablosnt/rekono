"""Django admin interface configuration for reporting models.

Registers reporting models with the Django admin interface for
administrative management and debugging purposes.
"""

from django.contrib import admin

from reporting.models import Report

admin.site.register(Report)

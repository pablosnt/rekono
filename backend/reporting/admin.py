"""Registration of the report model in the Django admin site."""

from django.contrib import admin

from reporting.models import Report

admin.site.register(Report)

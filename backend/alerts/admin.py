"""Registration of the alert model in the Django admin site."""

from django.contrib import admin

from alerts.models import Alert

admin.site.register(Alert)

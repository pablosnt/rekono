"""Registration of the target port model in the Django admin site."""

from django.contrib import admin

from target_ports.models import TargetPort

admin.site.register(TargetPort)

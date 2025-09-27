"""Django admin configuration for target ports module.

Registers the TargetPort model with Django admin interface for administrative
management of target port configurations. Provides basic CRUD operations for target ports.
"""

from django.contrib import admin

from target_ports.models import TargetPort

admin.site.register(TargetPort)

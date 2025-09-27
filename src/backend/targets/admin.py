"""Django admin configuration for targets module.

Registers the Target model with Django admin interface for administrative
management of target configurations. Provides basic CRUD operations for targets.
"""

from django.contrib import admin

from targets.models import Target

admin.site.register(Target)

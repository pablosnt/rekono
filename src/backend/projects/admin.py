"""Django admin interface configuration for project models.

Registers project models with Django admin interface for administrative
management and debugging of project-related data.
"""

from django.contrib import admin

from projects.models import Project

admin.site.register(Project)

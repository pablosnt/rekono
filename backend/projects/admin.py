"""Django admin configuration for project models.

Registers the Project model with the Django admin interface for administrative
management and debugging of project-related data.
"""

from django.contrib import admin

from projects.models import Project

admin.site.register(Project)

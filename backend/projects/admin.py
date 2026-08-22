"""Registration of the project model in the Django admin site."""

from django.contrib import admin

from projects.models import Project

admin.site.register(Project)

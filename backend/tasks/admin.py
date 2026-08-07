"""Registration of the task model in the Django admin site."""

from django.contrib import admin

from tasks.models import Task

admin.site.register(Task)

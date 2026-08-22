"""Registration of the execution model in the Django admin site."""

from django.contrib import admin

from executions.models import Execution

admin.site.register(Execution)

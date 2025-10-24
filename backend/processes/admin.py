"""Django admin interface configuration for process management.

Registers process and step models with the Django admin interface for
administrative management of security testing workflows and process steps.
"""

from django.contrib import admin

from processes.models import Process, Step

admin.site.register(Process)
admin.site.register(Step)

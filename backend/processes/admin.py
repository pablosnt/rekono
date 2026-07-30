"""Django admin configuration for processes module.

Registers the Process and Step models with the Django admin interface for
administrative management of security testing workflow definitions and steps.
"""

from django.contrib import admin

from processes.models import Process, Step

admin.site.register(Process)
admin.site.register(Step)

"""Registration of the process models in the Django admin site."""

from django.contrib import admin

from processes.models import Process, Step

admin.site.register(Process)
admin.site.register(Step)

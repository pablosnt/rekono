"""Django admin configuration for tools module.

Registers tools module models with Django admin interface for
administrative management of tools, configurations, and related objects.
"""

from django.contrib import admin

from tools.models import Argument, Configuration, Input, Intensity, Output, Tool

admin.site.register(Tool)
admin.site.register(Configuration)
admin.site.register(Argument)
admin.site.register(Input)
admin.site.register(Output)
admin.site.register(Intensity)

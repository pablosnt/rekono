"""Registration of the tool models in the Django admin site."""

from django.contrib import admin

from tools.models import Argument, Configuration, Input, Intensity, Output, Tool

admin.site.register(Tool)
admin.site.register(Configuration)
admin.site.register(Argument)
admin.site.register(Input)
admin.site.register(Output)
admin.site.register(Intensity)

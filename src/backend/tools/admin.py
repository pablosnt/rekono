from django.contrib import admin

from tools.models import Configuration, Input, Intensity, Output, Tool

admin.site.register(Tool)
admin.site.register(Configuration)
admin.site.register(Input)
admin.site.register(Output)
admin.site.register(Intensity)

from django.contrib import admin
from tools.models import Tool, Configuration, Input, Output, Intensity

# Register your models here.

admin.site.register(Tool)
admin.site.register(Configuration)
admin.site.register(Input)
admin.site.register(Output)
admin.site.register(Intensity)

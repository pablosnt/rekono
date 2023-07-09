from django.contrib import admin

from targets.models import Target, TargetPort

# Register your models here.

admin.site.register(Target)
admin.site.register(TargetPort)

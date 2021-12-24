from django.contrib import admin
from targets.models import Target, TargetEndpoint, TargetPort

# Register your models here.

admin.site.register(Target)
admin.site.register(TargetPort)
admin.site.register(TargetEndpoint)

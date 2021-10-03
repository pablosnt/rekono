from django.contrib import admin
from projects.models import Project, Target, TargetPort

# Register your models here.

admin.site.register(Project)
admin.site.register(Target)
admin.site.register(TargetPort)

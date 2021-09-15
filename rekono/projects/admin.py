from django.contrib import admin
from projects.models import Access, Project, Target, TargetPort

# Register your models here.

admin.site.register(Project)
admin.site.register(Target)
admin.site.register(TargetPort)
admin.site.register(Access)

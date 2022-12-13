from django.contrib import admin

from targets.models import (Target, TargetPort, TargetTechnology,
                            TargetVulnerability)

# Register your models here.

admin.site.register(Target)
admin.site.register(TargetPort)
admin.site.register(TargetTechnology)
admin.site.register(TargetVulnerability)

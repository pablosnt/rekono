from django.contrib import admin
from targets.models import (Target, TargetEndpoint, TargetPort,
                            TargetTechnology, TargetVulnerability)

# Register your models here.

admin.site.register(Target)
admin.site.register(TargetPort)
admin.site.register(TargetEndpoint)
admin.site.register(TargetTechnology)
admin.site.register(TargetVulnerability)

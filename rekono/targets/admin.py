from django.contrib import admin

from targets.models import (Target, TargetCredential, TargetPort,
                            TargetTechnology, TargetVulnerability)

# Register your models here.

admin.site.register(Target)
admin.site.register(TargetPort)
admin.site.register(TargetTechnology)
admin.site.register(TargetVulnerability)
admin.site.register(TargetCredential)

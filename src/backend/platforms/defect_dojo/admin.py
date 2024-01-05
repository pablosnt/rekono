from django.contrib import admin

from platforms.defect_dojo.models import (
    DefectDojoSettings,
    DefectDojoSync,
    DefectDojoTargetSync,
)

# Register your models here.

admin.register(DefectDojoSettings)
admin.register(DefectDojoSync)
admin.register(DefectDojoTargetSync)

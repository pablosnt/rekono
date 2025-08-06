from django.contrib import admin

from platforms.defectdojo.models import (
    DefectDojoSettings,
    DefectDojoSync,
    DefectDojoTargetSync,
)

admin.register(DefectDojoSettings)
admin.register(DefectDojoSync)
admin.register(DefectDojoTargetSync)

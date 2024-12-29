from django.contrib import admin
from platforms.defectdojo.models import (
    DefectDojoSettings,
    DefectDojoSync,
    DefectDojoTargetSync,
)

# Register your models here.

admin.register(DefectDojoSettings)
admin.register(DefectDojoSync)
admin.register(DefectDojoTargetSync)

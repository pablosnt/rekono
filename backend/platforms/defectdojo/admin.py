"""Registration of the DefectDojo models in the Django admin site."""

from django.contrib import admin

from platforms.defectdojo.models import DefectDojoSettings, DefectDojoSync, DefectDojoTargetSync

admin.site.register(DefectDojoSettings)
admin.site.register(DefectDojoSync)
admin.site.register(DefectDojoTargetSync)

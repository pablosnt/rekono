"""Django admin configuration for DefectDojo integration models.

Registers DefectDojo integration models with Django admin interface for
administrative management of integration settings and synchronization mappings.
"""

from django.contrib import admin

from platforms.defectdojo.models import DefectDojoSettings, DefectDojoSync, DefectDojoTargetSync

admin.site.register(DefectDojoSettings)
admin.site.register(DefectDojoSync)
admin.site.register(DefectDojoTargetSync)

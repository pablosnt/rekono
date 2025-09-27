"""Django admin configuration for VirusTotal platform models.

This module registers VirusTotal platform models with the Django admin interface
for administrative management of platform settings and configuration.
"""

from django.contrib import admin

from platforms.virustotal.models import VirusTotalSettings

admin.site.register(VirusTotalSettings)

"""Registration of the VirusTotal settings model in the Django admin site."""

from django.contrib import admin

from platforms.virustotal.models import VirusTotalSettings

admin.site.register(VirusTotalSettings)

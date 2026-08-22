"""Registration of the VulnCheck settings model in the Django admin site."""

from django.contrib import admin

from platforms.vulncheck.models import VulnCheckSettings

admin.site.register(VulnCheckSettings)

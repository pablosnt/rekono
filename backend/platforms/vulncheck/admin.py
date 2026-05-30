"""Django admin configuration for VulnCheck platform management.

Registers VulnCheck models with Django admin interface for administrative
management of platform settings and configuration.
"""

from django.contrib import admin

from platforms.vulncheck.models import VulnCheckSettings

admin.site.register(VulnCheckSettings)

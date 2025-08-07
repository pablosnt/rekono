"""Django admin configuration for NVD NIST platform management.

Registers NVD NIST models with Django admin interface for administrative
management of platform settings and configuration.
"""

from django.contrib import admin

from platforms.nvdnist.models import NvdNistSettings

admin.site.register(NvdNistSettings)

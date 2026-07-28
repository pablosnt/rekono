"""Django admin interface configuration for CVE Crowd platform management.

Registers CVE Crowd models with the Django admin interface for administrative
management of threat intelligence platform configuration and its trending CVE cache.
"""

from django.contrib import admin

from platforms.cvecrowd.models import CveCrowdCache, CveCrowdSettings

admin.site.register(CveCrowdSettings)
admin.site.register(CveCrowdCache)

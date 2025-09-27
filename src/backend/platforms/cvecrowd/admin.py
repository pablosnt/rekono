"""Django admin interface configuration for CVE Crowd platform management.

Registers CVE Crowd settings model with the Django admin interface for
administrative management of threat intelligence platform configuration.
"""

from django.contrib import admin

from platforms.cvecrowd.models import CveCrowdSettings

admin.site.register(CveCrowdSettings)

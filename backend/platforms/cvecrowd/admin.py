"""Registration of the CVE Crowd models in the Django admin site."""

from django.contrib import admin

from platforms.cvecrowd.models import CveCrowdCache, CveCrowdSettings

admin.site.register(CveCrowdSettings)
admin.site.register(CveCrowdCache)

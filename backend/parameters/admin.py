"""Registration of the input parameter models in the Django admin site."""

from django.contrib import admin

from parameters.models import InputTechnology, InputVulnerability

admin.site.register(InputTechnology)
admin.site.register(InputVulnerability)

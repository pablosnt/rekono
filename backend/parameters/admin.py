"""Django admin configuration for parameters module.

Registers input parameter models with Django admin interface for
administrative management of technology and vulnerability parameters.
"""

from django.contrib import admin

from parameters.models import InputTechnology, InputVulnerability

admin.site.register(InputTechnology)
admin.site.register(InputVulnerability)

"""Django admin configuration for authentication models.

Configures Django admin interface for authentication models, allowing
administrative management of authentication records.
"""

from django.contrib import admin

from authentications.models import Authentication

admin.site.register(Authentication)

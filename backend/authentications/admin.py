"""Registration of the authentication model in the Django admin site."""

from django.contrib import admin

from authentications.models import Authentication

admin.site.register(Authentication)

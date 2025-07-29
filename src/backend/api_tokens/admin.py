"""Admin configuration for API token models."""

from django.contrib import admin

from api_tokens.models import ApiToken

# Register your models here.

admin.site.register(ApiToken)

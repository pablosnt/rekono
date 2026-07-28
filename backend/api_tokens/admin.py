"""Django admin configuration for API token models.

Registers the ApiToken model with Django admin interface for
administrative management of API tokens.
"""

from django.contrib import admin

from api_tokens.models import ApiToken

admin.site.register(ApiToken)

"""Registration of the API token model in the Django admin site."""

from django.contrib import admin

from api_tokens.models import ApiToken

admin.site.register(ApiToken)

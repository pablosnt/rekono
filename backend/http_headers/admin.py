"""Registration of the HTTP header model in the Django admin site."""

from django.contrib import admin

from http_headers.models import HttpHeader

admin.site.register(HttpHeader)

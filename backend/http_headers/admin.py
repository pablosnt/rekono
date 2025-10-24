"""Django admin configuration for HTTP headers management.

Provides administrative interface for HTTP header management
with basic registration for the HttpHeader model.
"""

from django.contrib import admin

from http_headers.models import HttpHeader

admin.site.register(HttpHeader)

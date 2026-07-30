"""Django admin configuration for HTTP header management.

Registers the HttpHeader model with the Django admin interface for
administrative management of header configurations across the global,
user-specific, and target-specific scopes used during security testing.
"""

from django.contrib import admin

from http_headers.models import HttpHeader

admin.site.register(HttpHeader)

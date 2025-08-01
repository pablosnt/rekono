"""Django admin configuration for findings models.

This module registers all finding models with the Django admin interface,
allowing administrators to view and manage security findings through
the Django admin panel.
"""

from django.contrib import admin

from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Host,
    Path,
    Port,
    Technology,
    Vulnerability,
)

admin.site.register(OSINT)
admin.site.register(Host)
admin.site.register(Port)
admin.site.register(Path)
admin.site.register(Technology)
admin.site.register(Vulnerability)
admin.site.register(Credential)
admin.site.register(Exploit)

from django.contrib import admin
from findings.models import (OSINT, Enumeration, Exploit, Host, HttpEndpoint,
                             Technology, Vulnerability, Credential)

# Register your models here.

admin.site.register(OSINT)
admin.site.register(Host)
admin.site.register(Enumeration)
admin.site.register(HttpEndpoint)
admin.site.register(Technology)
admin.site.register(Vulnerability)
admin.site.register(Credential)
admin.site.register(Exploit)

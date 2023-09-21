from django.contrib import admin
from findings.models import (OSINT, Credential, Path, Port, Exploit,
                             Host, Technology, Vulnerability)

# Register your models here.

admin.site.register(OSINT)
admin.site.register(Host)
admin.site.register(Port)
admin.site.register(Path)
admin.site.register(Technology)
admin.site.register(Vulnerability)
admin.site.register(Credential)
admin.site.register(Exploit)

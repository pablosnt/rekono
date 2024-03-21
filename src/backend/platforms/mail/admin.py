from django.contrib import admin

from platforms.mail.models import SMTPSettings

# Register your models here.

admin.site.register(SMTPSettings)

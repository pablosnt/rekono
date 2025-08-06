from django.contrib import admin

from platforms.mail.models import SMTPSettings

admin.site.register(SMTPSettings)

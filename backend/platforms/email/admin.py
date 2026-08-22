"""Registration of the SMTP settings model in the Django admin site."""

from django.contrib import admin

from platforms.email.models import SMTPSettings

admin.site.register(SMTPSettings)

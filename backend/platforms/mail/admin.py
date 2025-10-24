"""Django admin configuration for mail platform models.

Registers the SMTPSettings model with Django admin interface for
administrative management of email notification configuration.
"""

from django.contrib import admin

from platforms.mail.models import SMTPSettings

admin.site.register(SMTPSettings)

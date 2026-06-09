"""Django admin configuration for email platform models.

Registers the SMTPSettings model with the Django admin interface for
administrative management of SMTP email notification configuration.
"""

from django.contrib import admin

from platforms.email.models import SMTPSettings

admin.site.register(SMTPSettings)

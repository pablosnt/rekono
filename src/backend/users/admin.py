"""Django admin configuration for user models.

Registers User model with Django admin interface for administrative
user account management and monitoring.
"""

from django.contrib import admin

from users.models import User

admin.site.register(User)

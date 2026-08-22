"""Registration of the user model in the Django admin site."""

from django.contrib import admin

from users.models import User

admin.site.register(User)

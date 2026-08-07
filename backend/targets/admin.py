"""Registration of the target model in the Django admin site."""

from django.contrib import admin

from targets.models import Target

admin.site.register(Target)

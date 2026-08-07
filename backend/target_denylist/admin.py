"""Registration of the target denylist model in the Django admin site."""

from django.contrib import admin

from target_denylist.models import TargetDenylist

admin.site.register(TargetDenylist)

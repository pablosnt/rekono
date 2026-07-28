"""Django admin configuration for target denylist models.

Registers the TargetDenylist model with the Django admin interface for
administrative management of target exclusion entries.
"""

from django.contrib import admin

from target_denylist.models import TargetDenylist

admin.site.register(TargetDenylist)

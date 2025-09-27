"""Django admin configuration for execution models.

Configures Django admin interface for execution models, allowing
administrative monitoring and management of execution records.
"""

from django.contrib import admin

from executions.models import Execution

admin.site.register(Execution)

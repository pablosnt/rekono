"""Django admin configuration for input_types module.

Registers the InputType model with Django admin interface for administrative
management of input type configurations.
"""

from django.contrib import admin

from input_types.models import InputType

admin.register(InputType)

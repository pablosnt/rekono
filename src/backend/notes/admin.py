"""Django admin configuration for notes module.

Registers Note model with Django admin interface for administrative
management of notes and collaborative documentation.
"""

from django.contrib import admin

from notes.models import Note

admin.site.register(Note)

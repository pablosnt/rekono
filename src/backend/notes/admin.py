"""Django admin configuration for the notes app.

This module configures the Django admin interface for the Note model,
providing a web-based interface for managing note data and relationships.
"""

from django.contrib import admin

from notes.models import Note

admin.site.register(Note)

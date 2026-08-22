"""Registration of the note model in the Django admin site."""

from django.contrib import admin

from notes.models import Note

admin.site.register(Note)

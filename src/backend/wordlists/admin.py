"""Django admin configuration for wordlist models.

Registers wordlist models with the Django admin interface for
administrative management and monitoring.
"""

from django.contrib import admin

from wordlists.models import Wordlist

admin.site.register(Wordlist)

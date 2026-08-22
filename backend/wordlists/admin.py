"""Registration of the wordlist model in the Django admin site."""

from django.contrib import admin

from wordlists.models import Wordlist

admin.site.register(Wordlist)

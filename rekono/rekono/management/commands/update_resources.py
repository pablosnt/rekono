import os
from typing import Any

from django.core.management.base import BaseCommand
from resources.models import Wordlist


class Command(BaseCommand):
    '''Rekono command to initialize resources data.'''

    help = 'Initialize resources data'

    def handle(self, *args: Any, **options: Any) -> None:
        '''Initialize resources data.'''
        for wordlist in Wordlist.objects.all().filter(size=None):               # For each default wordlist
            if os.path.isfile(wordlist.path):                                   # If wordlist path exist
                with open(wordlist.path, 'rb+') as wordlist_file:               # Open uploaded file
                    wordlist.size = len(wordlist_file.readlines())              # Count entries from uploaded file
                    wordlist.save(update_fields=['size'])

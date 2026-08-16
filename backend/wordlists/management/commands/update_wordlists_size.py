"""Command that counts the words of the wordlist files."""

import os
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand

from wordlists.models import Wordlist


class Command(BaseCommand):
    """Command that updates the number of words of all the wordlists.

    The wordlist files live in the filesystem of the deployment, and the default ones
    are provided by the packages installed in it, so their size is calculated on
    every deployment instead of during the migrations, which only know about the
    wordlist metadata stored in the database.

    Attributes:
        help: Description of the command shown by the Django help.
    """

    help = "Update the number of words of the wordlists"

    def handle(self, *args: Any, **options: Any) -> None:
        """Count the words of each wordlist file whose content can be read.

        Args:
            *args: Not used, since the command takes no arguments.
            **options: Not used, since the command takes no options.
        """
        updated = 0
        for wordlist in Wordlist.objects.all():
            if Path(wordlist.path).is_file() and os.access(wordlist.path, os.R_OK):
                with open(wordlist.path, "rb") as wordlist_file:
                    new_size = len(wordlist_file.readlines())
                    if new_size != wordlist.size:
                        wordlist.size = new_size
                        wordlist.save(update_fields=["size"])
                        updated += 1
        self.stdout.write(self.style.SUCCESS(f"Size of {updated} wordlists has been updated"))

from typing import Any

from django.core.management.base import BaseCommand

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseCommand, BaseEncryptionKeyCommand):
    help = "Remove the configured encryption key to store all sensitive data as plain text in database"

    def handle(self, *args: Any, **options: Any) -> None:
        self.rotate_encrypted_values(lambda v: v, self.current_encryptor.decrypt, None)
        self.logger.info(f"Encryption key has been removed from {CONFIG.config_file}")

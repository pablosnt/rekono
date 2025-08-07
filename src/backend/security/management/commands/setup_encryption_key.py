from typing import Any

from django.core.management.base import BaseCommand

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseCommand, BaseEncryptionKeyCommand):
    help = "Configure an encryption key to keep sensitive data encrypted in the database"

    def handle(self, *args: Any, **options: Any) -> None:
        if CONFIG.encryption_key:
            self.error("Encryption key is already configured. Use rotate_encryption_key command to change it")
        new_encryptor, new_encryption_key = self.new_encryptor()
        self.rotate_encrypted_values(new_encryptor.encrypt, lambda v: v, new_encryption_key)
        self.logger.info(f"New encryption key has been stored in {CONFIG.config_file}")

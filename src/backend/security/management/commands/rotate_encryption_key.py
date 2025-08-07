from typing import Any

from django.core.management.base import BaseCommand

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseCommand, BaseEncryptionKeyCommand):
    help = "Rotate the configured encryption key"

    def handle(self, *args: Any, **options: Any) -> None:
        new_encryptor, new_encryption_key = self.new_encryptor()
        self.rotate_encrypted_values(new_encryptor.encrypt, self.current_encryptor.decrypt, new_encryption_key)
        self.logger.info(f"Encryption key has been rotated in {CONFIG.config_file}")

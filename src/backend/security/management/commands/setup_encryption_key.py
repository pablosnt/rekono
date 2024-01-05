import logging
import sys
from typing import Any

from django.core.management.base import BaseCommand

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand

logger = logging.getLogger()


class Command(BaseCommand, BaseEncryptionKeyCommand):
    help = (
        "Configure an encryption key to keep sensitive data encrypted in the database"
    )

    def handle(self, *args: Any, **options: Any) -> None:
        if CONFIG.encryption_key:
            logger.error(
                "Encryption key is already configured. Use rotate_encryption_key command to change it"
            )
            sys.exit(1)
        new_encryptor, new_encryption_key = self._get_new_encryptor()
        self._replace_encrypted_values(new_encryptor.encrypt, lambda v: v)
        self._configure_encryption_key(new_encryption_key)
        logger.info(f"New encryption key has been stored in {CONFIG.config_file}")

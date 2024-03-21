import logging
import sys
from typing import Any

from django.core.management.base import BaseCommand

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand

logger = logging.getLogger()


class Command(BaseCommand, BaseEncryptionKeyCommand):
    help = "Rotate the configured encryption key"

    def handle(self, *args: Any, **options: Any) -> None:
        if not CONFIG.encryption_key:
            logger.error(
                "Encryption key is not configured. Use setup_encryption_key command first to configure it"
            )
            sys.exit(1)
        new_encryptor, new_encryption_key = self._get_new_encryptor()
        self._replace_encrypted_values(
            new_encryptor.encrypt, self._get_current_encryptor().decrypt
        )
        self._configure_encryption_key(new_encryption_key)
        logger.info(f"Encryption key has been rotated in {CONFIG.config_file}")

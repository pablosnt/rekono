import sys
from typing import Any

from django.core.management.base import BaseCommand

from framework.logging import LoggingEntity
from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseCommand, BaseEncryptionKeyCommand, LoggingEntity):
    help = "Remove the configured encryption key to store all sensitive data as plain text in database"

    def handle(self, *args: Any, **options: Any) -> None:
        if not CONFIG.encryption_key:
            self.logger.error("Encryption key is not configured yet")
            sys.exit(1)
        self._replace_encrypted_values(lambda v: v, self._get_current_encryptor().decrypt)
        self._configure_encryption_key(None)
        self.logger.info(f"Encryption key has been removed from {CONFIG.config_file}")

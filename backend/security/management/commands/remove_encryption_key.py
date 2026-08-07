"""Command that removes the encryption key and stores the data as plain text."""

from typing import Any

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseEncryptionKeyCommand):
    """Command that decrypts all the sensitive data and clears the encryption key.

    Data still encrypted with the key at the time it is removed from configuration
    can never be decrypted again, so every value is converted to plain text within
    one database transaction, and the key is only cleared once that transaction has
    been committed. An interrupted removal rolls back and leaves every value
    encrypted with the key that is still configured.

    Attributes:
        help: Description of the command shown by the Django command framework.
    """

    help = "Remove the configured encryption key to store all sensitive data as plain text in database"

    def handle(self, *args: Any, **options: Any) -> None:
        """Decrypt all the sensitive data and remove the configured encryption key.

        Args:
            *args: Positional arguments of the command, forwarded to the base one.
            **options: Options of the command, forwarded to the base one.

        Raises:
            SystemExit: If no current encryption key is configured or the removal isn't confirmed.
        """
        if not CONFIG.encryption_key:
            self.error("Encryption key is not configured, so it can't be removed")
        super().handle(*args, **options)
        self.rotate_encrypted_values(lambda v: v, self.current_encryptor.decrypt, None)
        self.stdout.write(self.style.SUCCESS(f"Encryption key has been removed from {CONFIG.config_file}"))

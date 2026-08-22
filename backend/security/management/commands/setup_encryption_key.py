"""Command that configures the encryption key of a deployment that has none yet."""

from typing import Any

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseEncryptionKeyCommand):
    """Command that generates an encryption key and encrypts the existing data.

    All the values are encrypted within a single database transaction, so an
    interrupted setup leaves every value as plain text, matching a configuration
    file where no encryption key has been stored yet. The new key is only written
    to the configuration file once that transaction has been committed, and it is
    shown in the terminal beforehand, so the sensitive data can still be recovered
    by hand if that last write fails.

    Attributes:
        help: Description of the command shown by the Django command framework.
    """

    help = "Configure an encryption key to keep sensitive data encrypted in the database"

    def handle(self, *args: Any, **options: Any) -> None:
        """Generate the encryption key and encrypt all the sensitive data with it.

        The new key is written to the standard output, and never to the logs, so
        it isn't stored in any log file. It is shown before the sensitive data is
        encrypted, so it is available to recover that data by hand if the new key
        can't be written to the configuration file once the data has been
        encrypted with it.

        Args:
            *args: Positional arguments of the command, forwarded to the base one.
            **options: Options of the command, forwarded to the base one.

        Raises:
            SystemExit: If encryption is already configured or the setup isn't confirmed.
        """
        if CONFIG.encryption_key:
            self.error("Encryption key is already configured. Use rotate_encryption_key command to change it")
        super().handle(*args, **options)
        new_encryptor, new_encryption_key = self.new_encryptor()
        self.stdout.write(f"New encryption key: {new_encryption_key}")
        self.stdout.write(
            self.style.NOTICE(
                "If the rotation fails after this point, use it to recover the data lost during the process\n"
            )
        )
        self.rotate_encrypted_values(new_encryptor.encrypt, lambda v: v, new_encryption_key)
        self.stdout.write(self.style.SUCCESS(f"New encryption key has been stored in {CONFIG.config_file}"))

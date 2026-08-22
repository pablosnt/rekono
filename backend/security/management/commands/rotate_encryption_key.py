"""Command that replaces the encryption key with a new one."""

from typing import Any

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseEncryptionKeyCommand):
    """Command that re-encrypts all the sensitive data with a new encryption key.

    All the values are re-encrypted within a single database transaction, so an
    interrupted rotation leaves every value encrypted with the current key, which
    is still the one stored in the configuration file. The new key is only written
    to the configuration file once that transaction has been committed, and it is
    shown in the terminal beforehand, so the sensitive data can still be recovered
    by hand if that last write fails.

    Attributes:
        help: Description of the command shown by the Django command framework.
    """

    help = "Rotate the configured encryption key"

    def handle(self, *args: Any, **options: Any) -> None:
        """Generate a new encryption key and re-encrypt all the sensitive data.

        The new key is written to the standard output, and never to the logs, so
        it isn't stored in any log file. It is shown before the rotation starts,
        so it is available to recover the sensitive data by hand if the new key
        can't be written to the configuration file once the data has been
        re-encrypted with it.

        Args:
            *args: Positional arguments of the command, forwarded to the base one.
            **options: Options of the command, forwarded to the base one.

        Raises:
            SystemExit: If no current encryption key is configured or the rotation isn't confirmed.
        """
        # Current key is checked before generating a new one, to avoid showing a key that won't be used
        current_decryptor = self.current_encryptor.decrypt
        super().handle(*args, **options)
        new_encryptor, new_encryption_key = self.new_encryptor()
        self.stdout.write(f"New encryption key: {new_encryption_key}")
        self.stdout.write(
            self.style.NOTICE(
                "If the rotation fails after this point, use it to recover the data lost during the process\n"
            )
        )
        self.rotate_encrypted_values(new_encryptor.encrypt, current_decryptor, new_encryption_key)
        self.stdout.write(self.style.SUCCESS(f"Encryption key has been rotated in {CONFIG.config_file}"))

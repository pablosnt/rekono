"""Django management command for rotating encryption keys in production.

Securely rotates the encryption key used for sensitive data by decrypting all
encrypted fields with the old key and re-encrypting them with a new key.
This command is essential for regular security maintenance and compliance.
"""

from typing import Any

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseEncryptionKeyCommand):
    """Django management command to rotate database encryption keys.

    Performs secure key rotation by decrypting all sensitive data with the
    current encryption key and re-encrypting it with a newly generated key.
    This operation maintains data security while updating encryption keys.

    Security Process:
        1. Validates current encryption key is configured
        2. Warns about database backups and asks for confirmation
        3. Generates a new cryptographically secure encryption key
        4. Shows the new encryption key in the terminal
        5. Decrypts all sensitive data using the current key
        6. Re-encrypts all data using the new key
        7. Updates the configuration with the new key
        8. Logs successful completion for audit trails

    All the values are re-encrypted within a single database transaction, so an
    interrupted rotation leaves every value encrypted with the current key, which
    is still the one stored in the configuration file. The new key is only written
    to the configuration file once that transaction has been committed, and it is
    shown in the terminal beforehand, so the sensitive data can still be recovered
    by hand if that last write fails.

    Usage:
        python manage.py rotate_encryption_key

    Performance Notes:
        - Processes all encrypted fields in the database
        - May take considerable time for large datasets
        - Recommended to run during maintenance windows
        - Database backup required before rotation

    Attributes:
        help (str): Django management command help text describing the operation.
    """

    help = "Rotate the configured encryption key"

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the encryption key rotation process.

        Decrypts all encrypted data with the current key and re-encrypts
        it with a newly generated key, updating the system configuration.

        The new key is written to the standard output, and never to the logs, so
        it isn't stored in any log file. It is shown before the rotation starts,
        so it is available to recover the sensitive data by hand if the new key
        can't be written to the configuration file once the data has been
        re-encrypted with it.

        Args:
            *args (Any): Positional arguments from Django command framework.
            **options (Any): Keyword arguments from Django command framework.

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

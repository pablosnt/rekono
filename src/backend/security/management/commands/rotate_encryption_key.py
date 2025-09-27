"""Django management command for rotating encryption keys in production.

Securely rotates the encryption key used for sensitive data by decrypting all
encrypted fields with the old key and re-encrypting them with a new key.
This command is essential for regular security maintenance and compliance.
"""

from typing import Any

from django.core.management.base import BaseCommand

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseCommand, BaseEncryptionKeyCommand):
    """Django management command to rotate database encryption keys.

    Performs secure key rotation by decrypting all sensitive data with the
    current encryption key and re-encrypting it with a newly generated key.
    This operation maintains data security while updating encryption keys.

    Security Process:
        1. Validates current encryption key is configured and valid
        2. Generates a new cryptographically secure encryption key
        3. Decrypts all sensitive data using the current key
        4. Re-encrypts all data using the new key
        5. Updates the configuration with the new key
        6. Logs successful completion for audit trails

    Usage:
        python manage.py rotate_encryption_key

    Performance Notes:
        - Processes all encrypted fields in the database
        - May take considerable time for large datasets
        - Recommended to run during maintenance windows
        - Database backup recommended before rotation

    Attributes:
        help (str): Django management command help text describing the operation.
    """

    help = "Rotate the configured encryption key"

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the encryption key rotation process.

        Decrypts all encrypted data with the current key and re-encrypts
        it with a newly generated key, updating the system configuration.

        Args:
            *args (Any): Positional arguments from Django command framework.
            **options (Any): Keyword arguments from Django command framework.

        Raises:
            SystemExit: If no current encryption key is configured.
        """
        new_encryptor, new_encryption_key = self.new_encryptor()
        self.rotate_encrypted_values(new_encryptor.encrypt, self.current_encryptor.decrypt, new_encryption_key)
        self.logger.info(f"Encryption key has been rotated in {CONFIG.config_file}")

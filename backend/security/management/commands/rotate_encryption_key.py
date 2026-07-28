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
        1. Validates current encryption key is configured
        2. Generates a new cryptographically secure encryption key
        3. Decrypts all sensitive data using the current key
        4. Re-encrypts all data using the new key
        5. Updates the configuration with the new key
        6. Logs successful completion for audit trails

    Each value is saved to the database as soon as it has been decrypted with
    the current key and re-encrypted with the new one, but the configuration
    file is only updated with the new key after every encrypted value has been
    processed. If the command is interrupted before it finishes, the values
    processed so far are already encrypted with the new key while the
    configuration still holds the old one, leaving the database in a mixed state
    that the command cannot repair on a later run, because it would then try to
    decrypt those values with the old key.

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

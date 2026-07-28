"""Django management command for setting up encryption key on fresh deployments.

Initializes encryption for sensitive data in the database by generating a new
encryption key and encrypting all existing sensitive fields with it. This
command is intended for deployments where no encryption key is yet configured.
"""

from typing import Any

from django.core.management.base import BaseCommand

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseCommand, BaseEncryptionKeyCommand):
    """Django management command to set up database encryption.

    Configures a new encryption key for the Rekono platform and encrypts all
    existing sensitive data in the database. This command is designed for
    initial deployment setup when no encryption key is currently configured.

    Security Process:
        1. Validates no encryption key is currently configured
        2. Generates a new cryptographically secure encryption key
        3. Encrypts all existing sensitive data using the new key
        4. Stores the encryption key in the configuration file
        5. Logs successful completion for audit trails

    Usage:
        python manage.py setup_encryption_key

    Performance Notes:
        - Processes all encryptable fields in the database
        - May take considerable time for large datasets
        - Recommended to run during maintenance windows
        - Database backup recommended before running this command

    Attributes:
        help (str): Django management command help text describing the operation.
    """

    help = "Configure an encryption key to keep sensitive data encrypted in the database"

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the encryption setup process.

        Validates the current state, generates a new encryption key, and
        encrypts all sensitive data in the database.

        Args:
            *args (Any): Positional arguments from Django command framework.
            **options (Any): Keyword arguments from Django command framework.

        Raises:
            SystemExit: If encryption is already configured.
        """
        if CONFIG.encryption_key:
            self.error("Encryption key is already configured. Use rotate_encryption_key command to change it")
        new_encryptor, new_encryption_key = self.new_encryptor()
        self.rotate_encrypted_values(new_encryptor.encrypt, lambda v: v, new_encryption_key)
        self.logger.info(f"New encryption key has been stored in {CONFIG.config_file}")

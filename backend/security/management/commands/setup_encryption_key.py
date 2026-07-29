"""Django management command for setting up encryption key on fresh deployments.

Initializes encryption for sensitive data in the database by generating a new
encryption key and encrypting all existing sensitive fields with it. This
command is intended for deployments where no encryption key is yet configured.
"""

from typing import Any

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseEncryptionKeyCommand):
    """Django management command to set up database encryption.

    Configures a new encryption key for the Rekono platform and encrypts all
    existing sensitive data in the database. This command is designed for
    initial deployment setup when no encryption key is currently configured.

    Security Process:
        1. Validates no encryption key is currently configured
        2. Warns about database backups and asks for confirmation
        3. Generates a new cryptographically secure encryption key
        4. Shows the new encryption key in the terminal
        5. Encrypts all existing sensitive data using the new key
        6. Stores the encryption key in the configuration file
        7. Logs successful completion for audit trails

    All the values are encrypted within a single database transaction, so an
    interrupted setup leaves every value as plain text, matching a configuration
    file where no encryption key has been stored yet. The new key is only written
    to the configuration file once that transaction has been committed, and it is
    shown in the terminal beforehand, so the sensitive data can still be recovered
    by hand if that last write fails.

    Usage:
        python manage.py setup_encryption_key

    Performance Notes:
        - Processes all encryptable fields in the database
        - May take considerable time for large datasets
        - Recommended to run during maintenance windows
        - Database backup required before running this command

    Attributes:
        help (str): Django management command help text describing the operation.
    """

    help = "Configure an encryption key to keep sensitive data encrypted in the database"

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the encryption setup process.

        Validates the current state, generates a new encryption key, and
        encrypts all sensitive data in the database.

        The new key is written to the standard output, and never to the logs, so
        it isn't stored in any log file. It is shown before the sensitive data is
        encrypted, so it is available to recover that data by hand if the new key
        can't be written to the configuration file once the data has been
        encrypted with it.

        Args:
            *args (Any): Positional arguments from Django command framework.
            **options (Any): Keyword arguments from Django command framework.

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

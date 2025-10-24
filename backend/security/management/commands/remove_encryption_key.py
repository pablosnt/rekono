"""Django management command for removing database encryption.

Decrypts all sensitive data and removes the encryption key configuration,
converting the database back to plain text storage. This command should only
be used in specific scenarios like development or compliance requirements.
"""

from typing import Any

from django.core.management.base import BaseCommand

from rekono.settings import CONFIG
from security.management.commands.encryption_key import BaseEncryptionKeyCommand


class Command(BaseCommand, BaseEncryptionKeyCommand):
    """Django management command to remove database encryption.

    Decrypts all sensitive data in the database and removes the encryption key
    configuration, reverting to plain text storage. This command should be used
    with extreme caution and only in specific scenarios.

    Security Process:
        1. Validates current encryption key is configured and valid
        2. Decrypts all sensitive data using the current key
        3. Stores decrypted data as plain text in database
        4. Removes encryption key from configuration
        5. Logs operation completion for audit trails

    Usage:
        python manage.py remove_encryption_key

    Security Warnings:
        - Results in sensitive data stored as plain text in database
        - Significantly reduces data security posture
        - Should only be used in specific compliance or development scenarios
        - Consider encryption alternatives before using this command
        - Ensure proper database security controls are in place

    Use Cases:
        - Development environments where encryption impedes debugging
        - Compliance requirements for specific audit scenarios
        - Migration to alternative encryption systems
        - Troubleshooting encryption-related issues

    Recommendations:
        - Backup database before running this command
        - Review security policies before removing encryption
        - Consider database-level encryption alternatives
        - Document business justification for encryption removal

    Attributes:
        help (str): Django management command help text describing the operation.
    """

    help = "Remove the configured encryption key to store all sensitive data as plain text in database"

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the encryption removal process.

        Decrypts all sensitive data using the current key and removes
        the encryption key from system configuration.

        Args:
            *args (Any): Positional arguments from Django command framework.
            **options (Any): Keyword arguments from Django command framework.

        Raises:
            SystemExit: If no current encryption key is configured.
        """
        self.rotate_encrypted_values(lambda v: v, self.current_encryptor.decrypt, None)
        self.logger.info(f"Encryption key has been removed from {CONFIG.config_file}")

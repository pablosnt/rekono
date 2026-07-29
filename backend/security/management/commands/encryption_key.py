"""Base class for encryption key management commands.

Provides common functionality for Django management commands that handle
encryption key operations including key generation, rotation, and data
migration. This module implements secure key management operations for
production deployments.
"""

import sys
from typing import Any, Callable

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from framework.logging import LoggingEntity
from framework.models import BaseEncrypted
from rekono.settings import CONFIG
from security.cryptography import Crypto


class BaseEncryptionKeyCommand(BaseCommand, LoggingEntity):
    """Base class providing common encryption key management functionality.

    Implements shared functionality for Django management commands that handle
    encryption key operations. Provides utilities for key validation, generation,
    and secure data migration during key rotation operations.

    Features:
        - Database backup warning and confirmation before any encryption key operation
        - Current encryption key validation and access
        - New encryption key generation
        - Secure data migration during key rotations
        - Error handling with logging and exit codes
        - Database-wide encrypted field processing
    """

    def handle(self, *args: Any, **options: Any) -> None:
        """Warn about the need of a database backup and ask for confirmation.

        Every encryption key command rewrites sensitive data across the whole
        database, so subclasses must call this implementation from their own handle
        method, once their own preconditions have been validated and before any
        value is processed. That way the user is only asked to confirm operations
        that can actually be performed.

        Args:
            *args (Any): Positional arguments from Django command framework.
            **options (Any): Keyword arguments from Django command framework.

        Raises:
            SystemExit: If the operation isn't confirmed by the user.
        """
        self.stdout.write(
            self.style.WARNING(
                "Back up the database before any operation over your encryption key. If something fails during the process, sensitive data could be lost"
            )
        )
        if input("Do you want to continue? [y/N] ").lower() not in ["y", "yes"]:
            self.error("Operation cancelled by the user")
        self.stdout.write("")

    @property
    def current_encryptor(self) -> Crypto:
        """Get the Crypto instance for the current encryption key.

        Reads the encryption key from the Rekono configuration file and validates
        that one is configured before constructing the Crypto instance, since
        Crypto requires a valid key to encrypt or decrypt.

        Returns:
            Crypto: Crypto instance configured with the current encryption key.

        Raises:
            SystemExit: If no encryption key is configured.
        """
        if not CONFIG.encryption_key:
            self.error("Encryption key is not configured. Use setup_encryption_key command first to configure it")
        return Crypto(CONFIG.encryption_key)

    def error(self, message: str, exit_code: int = 1) -> None:
        """Log error message and exit with specified code.

        Logs an error message and terminates the command execution with
        the specified exit code for proper error handling in scripts.

        Args:
            message (str): Error message to log and display.
            exit_code (int): System exit code (default: 1).
        """
        self.stdout.write(self.style.ERROR(message))
        sys.exit(exit_code)

    def new_encryptor(self) -> tuple[Crypto, str]:
        """Generate a new encryption key and encryptor.

        Creates a new cryptographically secure encryption key and returns
        both the configured Crypto instance and the raw key string.

        Returns:
            tuple[Crypto, str]: Tuple of (Crypto instance, raw key string).
        """
        new_encryption_key = Crypto.generate_encryption_key()
        return Crypto(new_encryption_key), new_encryption_key

    @transaction.atomic()
    def rotate_encrypted_values(
        self, new_value_processor: Callable, old_value_processor: Callable, new_encryption_key: str | None
    ) -> None:
        """Rotate encryption for all encrypted values in the database.

        Performs secure migration of all encrypted data in the database by
        processing each encrypted field through old and new value processors.
        This enables key rotation, encryption setup, and encryption removal.

        Every value is processed within a single database transaction, so an
        interrupted or failed operation rolls back all the values processed so far
        and leaves them encrypted with the original key. That keeps the database
        consistent with the encryption key stored in the configuration file, which
        can only be updated once the transaction has been committed, and makes the
        command safe to run again.

        Process:
            1. Iterate through all Django models
            2. Identify models with encrypted fields
            3. Process each encrypted value through the transformation pipeline
            4. Update the database with the new encrypted values
            5. Write new_encryption_key to the Rekono configuration file, or clear the
               configured encryption key entirely when new_encryption_key is None

        Args:
            new_value_processor (Callable): Function to process values with new key.
            old_value_processor (Callable): Function to process values with old key.
            new_encryption_key (str | None): Encryption key to store in the configuration
                file, or None to remove the configured encryption key.

        Raises:
            SystemExit: If some value can't be decrypted with the configured encryption key.
        """
        try:
            for model in apps.get_models():
                if not issubclass(model, BaseEncrypted):
                    continue
                for entity in model.objects.all():
                    encrypted_value = getattr(entity, entity._encrypted_field)
                    if encrypted_value:  # Empty values are skipped, since there is nothing to decrypt or re-encrypt
                        setattr(
                            entity,
                            entity._encrypted_field,
                            new_value_processor(old_value_processor(encrypted_value)),
                        )
                        entity.save(update_fields=[entity._encrypted_field])
        except Exception:
            self.error(
                "Some values can't be decrypted with the configured encryption key. No changes have been applied"
            )
        # Only updated after the transaction has been committed, so the configured key always matches the database
        CONFIG._encryption_key.update(CONFIG, new_encryption_key)

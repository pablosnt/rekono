"""Base class for encryption key management commands.

Provides common functionality for Django management commands that handle
encryption key operations including key generation, rotation, and data
migration. This module implements secure key management operations for
production deployments.
"""

import sys
from typing import Callable

from django.apps import apps

from framework.logging import LoggingEntity
from framework.models import BaseEncrypted
from rekono.settings import CONFIG
from security.cryptography import Crypto


class BaseEncryptionKeyCommand(LoggingEntity):
    """Base class providing common encryption key management functionality.

    Implements shared functionality for Django management commands that handle
    encryption key operations. Provides utilities for key validation, generation,
    and secure data migration during key rotation operations.

    Features:
        - Current encryption key validation and access
        - New encryption key generation
        - Secure data migration during key rotations
        - Error handling with logging and exit codes
        - Database-wide encrypted field processing
    """

    @property
    def current_encryptor(self) -> Crypto:
        """Get the current encryption key validator.

        Returns a Crypto instance configured with the current encryption key.
        Validates that an encryption key is configured before proceeding.

        Returns:
            Crypto: Configured crypto instance for current key.

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
        self.logger.error(message)
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

    def rotate_encrypted_values(
        self, new_value_processor: Callable, old_value_processor: Callable, new_encryption_key: str | None
    ) -> None:
        """Rotate encryption for all encrypted values in the database.

        Performs secure migration of all encrypted data in the database by
        processing each encrypted field through old and new value processors.
        This enables key rotation, encryption setup, and encryption removal.

        Process:
            1. Iterate through all Django models
            2. Identify models with encrypted fields
            3. Process each encrypted value through the transformation pipeline
            4. Update the database with the new encrypted values
            5. Update the system encryption key configuration

        Args:
            new_value_processor (Callable): Function to process values with new key.
            old_value_processor (Callable): Function to process values with old key.
            new_encryption_key (str | None): New encryption key to configure.
        """
        for model in apps.get_models():
            if not issubclass(model, BaseEncrypted):
                continue
            for entity in model.objects.all():
                encrypted_value = getattr(entity, entity._encrypted_field)
                if encrypted_value:
                    setattr(
                        entity,
                        entity._encrypted_field,
                        new_value_processor(old_value_processor(encrypted_value)),
                    )
                    entity.save(update_fields=[entity._encrypted_field])
        CONFIG._encryption_key.update(CONFIG, new_encryption_key)

"""Base command shared by the commands that manage the encryption key.

The three of them, setup, rotation, and removal, rewrite every encrypted value of
the database, so the transaction handling and the update of the configuration file
are implemented once here.
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
    """Base command that rewrites all the encrypted values of the database."""

    def handle(self, *args: Any, **options: Any) -> None:
        """Warn about the need of a database backup and ask for confirmation.

        Every encryption key command rewrites sensitive data across the whole
        database, so subclasses must call this implementation from their own handle
        method, once their own preconditions have been validated and before any
        value is processed. That way the user is only asked to confirm operations
        that can actually be performed.

        Args:
            *args: Positional arguments of the command, unused here.
            **options: Options of the command, unused here.

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
        """The encryptor that uses the key currently stored in the configuration file.

        Raises:
            SystemExit: If no encryption key is configured, since Crypto requires a
                valid key to encrypt or decrypt.
        """
        if not CONFIG.encryption_key:
            self.error("Encryption key is not configured. Use setup_encryption_key command first to configure it")
        return Crypto(CONFIG.encryption_key)

    def error(self, message: str, exit_code: int = 1) -> None:
        """Report an error and stop the command with the given exit code.

        Args:
            message: Error shown to the user in the standard output.
            exit_code: Status code that the process exits with.
        """
        self.stdout.write(self.style.ERROR(message))
        sys.exit(exit_code)

    def new_encryptor(self) -> tuple[Crypto, str]:
        """Generate a new encryption key.

        Returns:
            The encryptor that uses the new key, and the key itself, which the
            commands show to the user before applying it.
        """
        new_encryption_key = Crypto.generate_encryption_key()
        return Crypto(new_encryption_key), new_encryption_key

    @transaction.atomic()
    def rotate_encrypted_values(
        self, new_value_processor: Callable, old_value_processor: Callable, new_encryption_key: str | None
    ) -> None:
        """Rewrite every encrypted value of the database and store the new key.

        Each value is decrypted by the old processor and encrypted again by the new
        one, which is what lets the same method set up, rotate, and remove the
        encryption.

        Every value is processed within a single database transaction, so an
        interrupted or failed operation rolls back all the values processed so far
        and leaves them encrypted with the original key. That keeps the database
        consistent with the encryption key stored in the configuration file, which
        can only be updated once the transaction has been committed, and makes the
        command safe to run again.

        Args:
            new_value_processor: Function that encrypts a value with the new key.
            old_value_processor: Function that decrypts a value with the old key.
            new_encryption_key: Encryption key to store in the configuration file, or
                None to remove the configured encryption key.

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

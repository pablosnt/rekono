import sys
from typing import Callable

from django.apps import apps

from framework.logging import LoggingEntity
from framework.models import BaseEncrypted
from rekono.settings import CONFIG
from security.cryptography import Crypto


class BaseEncryptionKeyCommand(LoggingEntity):
    @property
    def current_encryptor(self) -> Crypto:
        if not CONFIG.encryption_key:
            self.error("Encryption key is not configured. Use setup_encryption_key command first to configure it")
        return Crypto(CONFIG.encryption_key)

    def error(self, message: str, exit_code: int = 1) -> None:
        self.logger.error(message)
        sys.exit(exit_code)

    def new_encryptor(self) -> tuple[Crypto, str]:
        new_encryption_key = Crypto.generate_encryption_key()
        return Crypto(new_encryption_key), new_encryption_key

    def rotate_encrypted_values(
        self, new_value_processor: Callable, old_value_processor: Callable, new_encryption_key: str | None
    ) -> None:
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

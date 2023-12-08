import logging
from typing import Tuple

from django.apps import apps
from framework.models import BaseEncrypted
from rekono.properties import Property
from rekono.settings import CONFIG
from security.cryptography.encryption import Encryptor

logger = logging.getLogger()


class BaseEncryptionKeyCommand:
    def _get_current_encryptor(self) -> Encryptor:
        return Encryptor(CONFIG.encryption_key)

    def _get_new_encryptor(self) -> Tuple[Encryptor, str]:
        new_encryption_key = Encryptor.generate_encryption_key()
        return Encryptor(new_encryption_key), new_encryption_key

    def _replace_encrypted_values(
        self, new_value_processor: callable, old_value_processor: callable
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

    def _configure_encryption_key(self, new_encryption_key: str) -> None:
        CONFIG.encryption_key = new_encryption_key
        CONFIG._update_config_in_file(
            Property.ENCRYPTION_KEY.value[1], new_encryption_key
        )

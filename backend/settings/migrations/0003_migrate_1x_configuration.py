# Copies the configuration of version 1.x, kept in one system model, into the settings and the
# platform models that replaced it, so an upgrade keeps its Telegram token and DefectDojo setup

from typing import Any

from django.db import migrations

from rekono.settings import CONFIG
from security.cryptography import Crypto

def _encrypt(value: str | None) -> str | None:
    """Encrypt a version 1.x secret the way that the version 2.x models store it.

    BaseEncrypted builds its encryptor from the configured key, and stores the value as
    plain text when there is none, so this does the same instead of using the models,
    whose historical versions have none of that behaviour.

    Returns:
        The encrypted secret, the plain one when no encryption key is configured, or None
        when there is no secret to migrate.
    """
    if not value:
        return None
    return Crypto(CONFIG.encryption_key).encrypt(value) if CONFIG.encryption_key else value


def migrate_1x_configuration(apps: Any, schema_editor: Any) -> None:
    """Copy the version 1.x configuration into the models that replaced it.

    Version 1.x kept the whole configuration in one system model, which version 2.x split
    into the settings and the configuration of each platform. Its DefectDojo product type,
    test type and test names are dropped, since version 2.x builds those names itself and
    has no setting to keep them in.

    Args:
        apps: Registry of the historical models, given by the migration framework.
        schema_editor: Not used, since only data is migrated.
    """
    system = apps.get_model("settings", "System").objects.first()
    if not system:
        # A fresh installation has this table, created by the restored version 1.x migration, but
        # never any row in it
        return
    # The rows take the primary key of the version 2.x fixtures, and those apps skip their fixtures
    # when their model already has data, so the defaults don't overwrite the migrated configuration
    apps.get_model("settings", "Settings").objects.update_or_create(
        pk=1,
        defaults={"max_uploaded_file_mb": system.upload_files_max_mb},
    )
    apps.get_model("telegram_app", "TelegramSettings").objects.update_or_create(
        pk=1,
        defaults={"_token": _encrypt(system.telegram_bot_token)},
    )
    apps.get_model("defectdojo", "DefectDojoSettings").objects.update_or_create(
        pk=1,
        defaults={
            "server": system.defect_dojo_url,
            "_api_token": _encrypt(system.defect_dojo_api_key),
            "tls_validation": system.defect_dojo_verify_tls,
            "tag": system.defect_dojo_tag,
            # Version 1.x had no setting for this, so an upgrade keeps the format that it always sent
            "date_format": "%Y-%m-%d",
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0002_settings'),
        ('telegram_app', '0003_telegramsettings_alter_telegramchat_otp_and_more'),
        ('defectdojo', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_1x_configuration, migrations.RunPython.noop),
    ]

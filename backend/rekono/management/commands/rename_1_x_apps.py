from typing import Any

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from framework.logging import LoggingEntity

RENAMED_APPS = {
    "resources": "wordlists",
    "system": "settings",
    "telegram_bot": "telegram_app",
}
RENAMED_TABLES = {
    "resources_wordlist": "wordlists_wordlist",
    "resources_wordlist_liked_by": "wordlists_wordlist_liked_by",
    "system_system": "settings_system",
    "telegram_bot_telegramchat": "telegram_app_telegramchat",
}
MOVED_CONTENT_TYPES = {
    ("resources", "wordlist"): ("wordlists", "wordlist"),
    ("system", "system"): ("settings", "system"),
    ("telegram_bot", "telegramchat"): ("telegram_app", "telegramchat"),
    ("targets", "targetport"): ("target_ports", "targetport"),
}
RENAMED_PERMISSIONS = {"system": "settings"}


class Command(BaseCommand, LoggingEntity):
    """Command that renames the version 1.x apps of a database before it is migrated.

    Attributes:
        help: Description of the command shown by the Django help.
    """

    help = "Apply the version 2.x app names to a database created by version 1.x"

    def handle(self, *args: Any, **options: Any) -> None:
        """Apply every rename that the version 1.x database still needs.

        All the renames share one transaction, so a database is either fully renamed
        or left untouched for the command to be run again. A half renamed one would
        be migrated against the wrong names.

        Args:
            *args: Not used, since the command takes no arguments.
            **options: Not used, since the command takes no options.
        """
        with transaction.atomic():
            renames = (
                self._rename_tables()
                + self._rename_recorded_migrations()
                + self._move_content_types()
                + self._rename_permissions()
            )
        if renames:
            self.stdout.write(self.style.SUCCESS(f"Applied {renames} version 2.x names to the database"))
        else:
            self.stdout.write("Database has no version 1.x names to rename")

    def _rename_tables(self) -> int:
        """Rename the tables whose name carries the app that owned them in version 1.x.

        Returns:
            The number of tables that were renamed.
        """
        existing = connection.introspection.table_names()
        renamed = 0
        for old_table, new_table in RENAMED_TABLES.items():
            if old_table not in existing or new_table in existing:
                continue
            with connection.cursor() as cursor:
                cursor.execute(f"ALTER TABLE {connection.ops.quote_name(old_table)} RENAME TO {connection.ops.quote_name(new_table)}")
            self.logger.info(f"[DB Upgrade] Table {old_table} renamed to {new_table}")
            renamed += 1
        return renamed

    def _rename_recorded_migrations(self) -> int:
        """Rename the apps of the migrations that version 1.x recorded as applied.

        Returns:
            The number of recorded migrations that were renamed.
        """
        renamed = 0
        with connection.cursor() as cursor:
            for old_app, new_app in RENAMED_APPS.items():
                cursor.execute(f"UPDATE django_migrations SET app = {new_app} WHERE app = {old_app}")
                if cursor.rowcount:
                    self.logger.info(f"[DB Upgrade] App {old_app} renamed to {new_app}")
                renamed += cursor.rowcount
        return renamed

    def _move_content_types(self) -> int:
        """Move the content types to the apps that own their models in version 2.x.

        Returns:
            The number of content types that were moved.
        """
        moved = 0
        with connection.cursor() as cursor:
            for (old_app, old_model), (new_app, new_model) in MOVED_CONTENT_TYPES.items():
                cursor.execute(f"SELECT 1 FROM django_content_type WHERE app_label = {new_app} AND model = {new_model}")
                if cursor.fetchone():
                    continue
                cursor.execute(f"UPDATE django_content_type SET app_label = {new_app}, model = {new_model} WHERE app_label = {old_app} AND model = {old_model}")
                if cursor.rowcount:
                    self.logger.info(f"[DB Upgrade] Content type {old_app}.{old_model} moved to {new_app}.{new_model}")
                moved += cursor.rowcount
        return moved

    def _rename_permissions(self) -> int:
        """Rename the permissions of the models that version 2.x renamed.

        Returns:
            The number of permissions that were renamed.
        """
        renamed = 0
        with connection.cursor() as cursor:
            for old_model, new_model in RENAMED_PERMISSIONS.items():
                for action in ["add", "change", "delete", "view"]:
                    cursor.execute(f"UPDATE auth_permission SET codename = {action}_{new_model} WHERE codename = {action}_{old_model}")
                    renamed += cursor.rowcount
                if renamed:
                    self.logger.info(f"[DB Upgrade] Permissions of {old_model} renamed to {new_model}")
        return renamed

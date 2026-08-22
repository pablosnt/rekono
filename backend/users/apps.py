"""Django app configuration of the users app.

It's the last app loaded by Django, since the groups that it creates need the
permissions of all the other models to exist already.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from security.authorization.roles import ROLES, Role


class UsersConfig(AppConfig):
    """Configuration of the users app.

    Attributes:
        name: Name of the app in the Django app registry.
    """

    name = "users"

    def ready(self) -> None:
        """Schedule the groups of the roles to be created after each migration."""
        post_migrate.connect(self.initialize_user_groups, sender=self)

    def initialize_user_groups(self, **kwargs: Any) -> None:
        """Create the group of each role and set the permissions that it grants.

        ROLES is the only source of truth for group permissions, so a role removed
        from an entry loses that permission on the next migration, and any permission
        granted to a group outside ROLES is discarded.

        Args:
            **kwargs: Arguments sent by the post_migrate signal.
        """
        # Models are fetched from the historical app registry passed by the signal,
        # not imported directly, so they match the schema at this migration state
        group_model = kwargs["apps"].get_model(app_label="auth", model_name="group")
        permission_model = kwargs["apps"].get_model(app_label="auth", model_name="permission")
        groups = {}
        role_permissions = {}
        for role in Role.values:
            groups[role], _ = group_model.objects.get_or_create(name=role)
            role_permissions[role] = []
        for entity, permissions in ROLES.items():
            for permission, assigned_roles in permissions.items():
                permission = permission_model.objects.get(codename=f"{permission}_{entity}")
                for assigned_role in assigned_roles:
                    role_permissions[assigned_role.value].append(permission)
        for role, permissions in role_permissions.items():
            groups[role].permissions.set(permissions)

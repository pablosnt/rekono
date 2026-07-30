"""Django app configuration for the users module.

Configures the users application with automatic creation of authentication
groups and role-based permission assignments once database migrations
are complete.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp
from security.authorization.roles import ROLES, Role


class UsersConfig(BaseApp, AppConfig):
    """Django app configuration for the users module.

    Extends BaseApp and AppConfig to provide user-management-specific
    initialization, creating Django auth groups and assigning role-based
    permissions after migrations.

    Attributes:
        name (str): The name of the Django app
    """

    name = "users"

    def ready(self) -> None:
        """Initialize the users application when Django is ready.

        Connects the post-migrate signal to initialize user groups and permissions
        after database migrations are complete.
        """
        post_migrate.connect(self.initialize_user_groups, sender=self)

    def initialize_user_groups(self, **kwargs: Any) -> None:
        """Initialize user groups and assign permissions after database migration.

        Creates Django auth groups for each security role and replaces their
        permissions with the ones granted by the ROLES configuration. ROLES is the
        only source of truth for group permissions, so a role removed from an entry
        loses that permission on the next migration, and any permission granted to a
        group outside ROLES is discarded.

        Args:
            **kwargs (Any): Django post-migrate signal arguments containing app
                           registry and migration information.
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

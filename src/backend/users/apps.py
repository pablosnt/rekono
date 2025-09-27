"""Django app configuration for the users module.

Defines Django app configuration for the user management application
with BaseApp functionality and standard Django app configuration.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp
from security.authorization.roles import ROLES, Role


class UsersConfig(BaseApp, AppConfig):
    """Django app configuration for the users module.

    Configures the users Django app with BaseApp functionality
    and standard Django app configuration for user management.

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

        Creates Django auth groups for each security role and assigns appropriate
        permissions based on the ROLES configuration. This ensures proper role-based
        access control is established when the application starts.

        Args:
            **kwargs (Any): Django post-migrate signal arguments containing app
                           registry and migration information.
        """
        group_model = kwargs["apps"].get_model(app_label="auth", model_name="group")
        permission_model = kwargs["apps"].get_model(app_label="auth", model_name="permission")
        groups = {}
        for role in Role.values:
            groups[role], _ = group_model.objects.get_or_create(name=role)
        for entity, permissions in ROLES.items():
            for permission, assigned_roles in permissions.items():
                permission = permission_model.objects.get(codename=f"{permission}_{entity}")
                for assigned_role in assigned_roles:
                    groups[assigned_role].permissions.add(permission)

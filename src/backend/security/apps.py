"""Django application configuration for the security module.

Configures the security application with Django's application framework,
providing initialization and configuration for security components.
"""

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from framework.apps import BaseApp
from security.authorization.roles import ROLES, Role


class SecurityConfig(BaseApp, AppConfig):
    """Django application configuration for security components.

    Configures the security application within Django's application framework,
    enabling security middleware, authentication backends, and security utilities
    throughout the Rekono platform.

    Attributes:
        name (str): The application name identifier for Django's app registry.
    """

    name = "security"

    def ready(self) -> None:
        """Initialize the security application when Django is ready.

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

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from framework.apps import BaseApp
from security.authorization.roles import ROLES, Role


class UsersConfig(BaseApp, AppConfig):
    name = "users"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        post_migrate.connect(self.initialize_user_groups, sender=self)

    def initialize_user_groups(self, **kwargs: Any) -> None:
        """Initialize user groups in database."""
        group_model = kwargs["apps"].get_model(app_label="auth", model_name="group")
        permission_model = kwargs["apps"].get_model(
            app_label="auth", model_name="permission"
        )
        groups = {}
        for role in Role.values:
            groups[role], _ = group_model.objects.get_or_create(name=role)
        for entity, permissions in ROLES.items():
            for permission, assigned_roles in permissions.items():
                permission = permission_model.objects.get(
                    codename=f"{permission}_{entity}"
                )
                for assigned_role in assigned_roles:
                    groups[assigned_role].permissions.add(permission)

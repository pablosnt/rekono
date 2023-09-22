from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from security.authorization.roles import ROLES


class UsersConfig(AppConfig):
    name = "users"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Initialize user groups based on permissions after migration
        post_migrate.connect(self.initialize_user_groups, sender=self)

    def initialize_user_groups(self, **kwargs: Any) -> None:
        """Initialize user groups in database."""
        group_model = kwargs["apps"].get_model(app_label="auth", model_name="group")
        permission_model = kwargs["apps"].get_model(
            app_label="auth", model_name="permission"
        )
        for entity, permissions in ROLES.items():
            for permission, assigned_roles in permissions.items():
                permission = permission_model.objects.get(
                    codename=f"{permission}_{entity}"
                )
                for assigned_role in assigned_roles:
                    group, _ = group_model.objects.get_or_create(name=assigned_role)
                    group.permissions.add(permission)

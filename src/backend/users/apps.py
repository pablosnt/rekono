from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from security.authorization.roles import get_roles


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
        for role, permissions in get_roles().items():
            group, _ = group_model.objects.get_or_create(name=role)
            group_permissions = []
            for permission_id in permissions:  # For each permission
                # Get permission model
                permission = permission_model.objects.get(codename=permission_id)
                group_permissions.append(permission)
            group.permissions.set(group_permissions)

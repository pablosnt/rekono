from django.apps import AppConfig
from typing import Any
from security.authorization.roles import get_roles
from django.db.models.signals import post_migrate


class SecurityConfig(AppConfig):
    name = "security"

    def ready(self) -> None:
        """Run code as soon as the registry is fully populated."""
        # Initialize user groups based on permissions after migration
        post_migrate.connect(self.initialize_user_groups, sender=self)

    def initialize_user_groups(self, **kwargs: Any) -> None:
        """Initialize user groups in database."""
        # Get Group model
        group_model = kwargs["apps"].get_model(app_label="auth", model_name="group")
        # Get permission model
        permission_model = kwargs["apps"].get_model(
            app_label="auth", model_name="permission"
        )
        for role, permissions in get_roles().items():
            group, _ = group_model.objects.get_or_create(name=str(role))  # Create group
            permission_set = []
            for permission_id in permissions:  # For each permission
                # Get permission model
                permission = permission_model.objects.get(codename=permission_id)
                permission_set.append(permission)
            group.permissions.set(permission_set)  # Assignate permissions to the group

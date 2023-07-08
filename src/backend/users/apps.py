from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from security.authorization.roles import ROLES


class UsersConfig(AppConfig):
    '''Users Django application.'''

    name = 'users'

    def ready(self) -> None:
        '''Run code as soon as the registry is fully populated.'''
        # Initialize user groups based on permissions after migration
        post_migrate.connect(self.initialize_user_groups, sender=self)

    def initialize_user_groups(self, **kwargs: Any) -> None:
        '''Initialize user groups in database.'''
        group_model = kwargs['apps'].get_model(app_label='auth', model_name='group')                # Get Group model
        permission_model = kwargs['apps'].get_model(app_label='auth', model_name='permission')  # Get permission model
        for name, permissions in ROLES.items():                                 # For each role
            group, _ = group_model.objects.get_or_create(name=str(name))  # Create group
            permission_set = []
            for permission_name in permissions:                                 # For each permission name
                permission = permission_model.objects.get(codename=permission_name)     # Get permission model
                permission_set.append(permission)                               # Save permission in the permission set
            group.permissions.set(permission_set)                               # Assignate permissions to the group

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from authorization.groups.initialize import initialize_user_groups


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        post_migrate.connect(initialize_user_groups, sender=self)

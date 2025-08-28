"""Django app configuration for the users module.

Defines Django app configuration for the user management application
with BaseApp functionality and standard Django app configuration.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class UsersConfig(BaseApp, AppConfig):
    """Django app configuration for the users module.

    Configures the users Django app with BaseApp functionality
    and standard Django app configuration for user management.

    Attributes:
        name (str): The name of the Django app
    """

    name = "users"

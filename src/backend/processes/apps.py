"""Django application configuration for process management module.

Provides application configuration for the processes module with fixture
management and model registration for security testing workflow management.
"""

from typing import Any

from django.apps import AppConfig

from framework.apps import BaseApp


class ProcessesConfig(BaseApp, AppConfig):
    """Django application configuration for the processes module.

    Configures the processes application with fixture management and
    model registration for security testing workflow components.

    Attributes:
        name (str): Application name for Django registration
        skip_fixtures_if_model_exists (bool): Skip fixture loading if models exist
    """

    name = "processes"
    skip_fixtures_if_model_exists = True

    def _get_models(self) -> list[Any]:
        """Get the model classes for this application.

        Returns:
            list[Any]: List containing Process and Step model classes.
        """
        from processes.models import Process, Step

        return [Process, Step]

import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class ProcessesConfig(AppConfig):
    '''Processes Django application.'''

    name = 'processes'

    def ready(self) -> None:
        '''Run code as soon as the registry is fully populated.'''
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self.load_processes_models, sender=self)

    def load_processes_models(self, **kwargs: Any) -> None:
        '''Load tools fixtures in database.'''
        path = os.path.join(Path(__file__).resolve().parent, 'fixtures')        # Path to fixtures directory
        management.call_command(
            loaddata.Command(),
            os.path.join(path, '1_processes.json'),                             # Process entities
            os.path.join(path, '2_steps.json'),                                 # Step entities
        )

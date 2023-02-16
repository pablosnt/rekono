import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class ToolsConfig(AppConfig):
    '''Tool Django application.'''

    name = 'tools'

    def ready(self) -> None:
        '''Run code as soon as the registry is fully populated.'''
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self.load_tools_models, sender=self)
        # Needed here to ensure processes migration after tools migration
        post_migrate.connect(self.load_processes_models, sender=self)

    def load_tools_models(self, **kwargs: Any) -> None:
        '''Load tools fixtures in database.'''
        path = os.path.join(Path(__file__).resolve().parent, 'fixtures')        # Path to fixtures directory
        management.call_command(
            loaddata.Command(),
            os.path.join(path, '1_tools.json'),                                 # Tool entities
            os.path.join(path, '2_intensities.json'),                           # Intensity entities
            os.path.join(path, '3_configurations.json'),                        # Configuration entities
            os.path.join(path, '4_arguments.json'),                             # Argument entities
            os.path.join(path, '5_inputs.json'),                                # Input entities
            os.path.join(path, '6_outputs.json')                                # Output entities
        )

    def load_processes_models(self, **kwargs: Any) -> None:
        '''Load processes fixtures in database.'''
        from processes.models import Process, Step
        if Process.objects.exists() or Step.objects.exists():                   # Check if default data is loaded
            return
        # Path to fixtures directory
        path = os.path.join(Path(__file__).resolve().parent.parent, 'processes', 'fixtures')
        management.call_command(
            loaddata.Command(),
            os.path.join(path, '1_processes.json'),                             # Process entities
            os.path.join(path, '2_steps.json'),                                 # Step entities
        )

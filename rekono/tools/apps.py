import os
from pathlib import Path

from django.apps import AppConfig
from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class ToolsConfig(AppConfig):
    name = 'tools'

    def ready(self) -> None:
        post_migrate.connect(self.load_tools_model, sender=self)

    def load_tools_model(self, **kwargs):
        path = os.path.join(Path(__file__).resolve().parent, 'fixtures')
        management.call_command(
            loaddata.Command(),
            os.path.join(path, '1_tools.json'),
            os.path.join(path, '2_intensities.json'),
            os.path.join(path, '3_configurations.json'),
            os.path.join(path, '4_arguments.json'),
            os.path.join(path, '5_inputs.json'),
            os.path.join(path, '6_outputs.json')
        )

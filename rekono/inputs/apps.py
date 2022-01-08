import os
from pathlib import Path

from django.apps import AppConfig
from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate


class InputsConfig(AppConfig):
    name = 'inputs'

    def ready(self) -> None:
        post_migrate.connect(self.load_inputs_model, sender=self)

    def load_inputs_model(self, **kwargs):
        path = os.path.join(Path(__file__).resolve().parent, 'fixtures')
        management.call_command(
            loaddata.Command(),
            os.path.join(path, '1_input_types.json')
        )

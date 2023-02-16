import os
from pathlib import Path
from typing import Any

from django.apps import AppConfig
from django.core import management
from django.core.management.commands import loaddata
from django.db.models.signals import post_migrate

from rekono.environment import RKN_DD_API_KEY, RKN_DD_URL, RKN_TELEGRAM_TOKEN
from rekono.settings import CONFIG


class SystemConfig(AppConfig):
    '''System Django application.'''

    name = 'system'

    def ready(self) -> None:
        '''Run code as soon as the registry is fully populated.'''
        # Configure fixtures to be loaded after migration
        post_migrate.connect(self.load_input_types_model, sender=self)

    def load_input_types_model(self, **kwargs: Any) -> None:
        '''Load input types fixtures in database.'''
        from system.models import System
        if System.objects.exists():                                             # Check if default data is loaded
            return
        path = os.path.join(Path(__file__).resolve().parent, 'fixtures')        # Path to fixtures directory
        management.call_command(
            loaddata.Command(),
            os.path.join(path, '1_default.json')                                # Default settings
        )
        self.load_existing_configuration()

    def load_existing_configuration(self) -> None:
        '''Load existing configuration from old Rekono versions.'''
        # --------------------------------------------------------------------------------------------------------------
        # DEPRECATED
        # The following configurations are mantained for compatibility reasons with the previous version.
        # This support will be removed in the next release, since this settings can be managed using the Settings page.
        # --------------------------------------------------------------------------------------------------------------
        from system.models import System
        system = System.objects.first()
        for environment_variable, file_property, system_field in [
            (RKN_TELEGRAM_TOKEN, CONFIG.TELEGRAM_TOKEN, 'telegram_bot_token'),
            (RKN_DD_URL, CONFIG.DD_URL, 'defect_dojo_url'),
            (RKN_DD_API_KEY, CONFIG.DD_API_KEY, 'defect_dojo_api_key'),
        ]:
            if os.getenv(environment_variable, file_property) and not getattr(system, system_field):
                setattr(system, system_field, os.getenv(environment_variable, file_property))
        system.save()

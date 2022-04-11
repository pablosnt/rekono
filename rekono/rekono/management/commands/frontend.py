from typing import Any

from django.core.management.base import BaseCommand

from rekono.settings import CONFIG, DEFECT_DOJO, FRONTEND_DIR, TELEGRAM_BOT


class Command(BaseCommand):
    '''Rekono command to initialize frontend configuration.'''

    help = 'Initialize frontend configuration'

    def handle(self, *args: Any, **options: Any) -> None:
        '''Initialize frontend configuration.'''
        CONFIG.load_config_in_frontend(                                         # Load configuration in frontend .env
            FRONTEND_DIR,
            {
                'VUE_APP_DEFECTDOJO': DEFECT_DOJO.get('URL') and DEFECT_DOJO.get('API_KEY'),    # Defect-Dojo configured
                'VUE_APP_DEFECTDOJO_HOST': DEFECT_DOJO['URL'],                  # Defect-Dojo URL to create links
                'VUE_APP_TELEGRAM_BOT': TELEGRAM_BOT,                           # Telegram bot name to show in the UI
            }
        )

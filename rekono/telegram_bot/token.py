import logging
import time
from typing import Callable

from system.models import System

logger = logging.getLogger()                                                    # Rekono logger


def wait_until_telegram_token_is_configured(sleep_time: int) -> None:
    '''Wait until Teelgram token is configured

    Args:
        sleep_time (int): Seconds to sleep
    '''
    token = System.objects.first().telegram_bot_token                           # Check the Telegram token
    if not token:
        logger.info('[Telegram Bot] Waiting until Telegram token is configured')
    while not token:
        time.sleep(sleep_time)                                                  # Sleep some time
        token = System.objects.first().telegram_bot_token                       # Check the Telegram token again


def handle_invalid_telegram_token(callback: Callable) -> None:
    '''Handle errors due to invalid Telegram token

    Args:
        callback (Callable): Function to call after the Telegram token is configured
    '''
    logger.error('[Telegram Bot] Error during Telegram bot authentication')
    system = System.objects.first()
    system.telegram_bot_token = None                                            # Remove Telegram token
    system.save(update_fields=['telegram_bot_token'])
    wait_until_telegram_token_is_configured(30)                                 # Wait until token is configured
    callback()

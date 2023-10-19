import logging
from typing import Any

from platforms.telegram_app.models import TelegramSettings
from telegram.error import Forbidden, InvalidToken
from telegram.ext import Updater

logger = logging.getLogger()


class BaseTelegram:
    def __init__(self) -> None:
        self.settings = TelegramSettings.objects.first()
        self.updater = self._get_updater()
        self.date_format = "%Y-%m-%d %H:%M:%S"

    def _get_updater(self) -> Any:
        if self.settings.token:
            try:
                return Updater(token=self.settings.token)
            except (InvalidToken, Forbidden):
                logger.error("[Telegram] Authentication error")
                self.settings.token = None
                self.settings.save(update_fields=["token"])
            except Exception:
                logger.error("[Telegram] Error creating updater")

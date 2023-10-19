from typing import List

from executions.models import Execution
from findings.framework.models import Finding
from framework.platforms import BaseNotification
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.models import TelegramChat
from platforms.telegram_app.templates import EXECUTION, FINDINGS, HEADER
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from users.models import User


class Telegram(BaseTelegram, BaseNotification):
    enable_field = "telegram_notifications"

    def is_available(self) -> bool:
        return bool(self.updater)

    def get_bot_name(self) -> str:
        return self.updater.bot.username if self.is_available() else None

    def _send_message(self, chat: TelegramChat, message: str) -> None:
        if self.is_available():
            self.updater.bot.send_message(
                chat.chat_id, text=message, parse_mode=ParseMode.MARKDOWN_V2
            )

    def _notify_execution(
        self, users: List[User], execution: Execution, findings: List[Finding]
    ) -> None:
        texts_by_type = {}
        for finding in findings:
            if finding.__class__ not in texts_by_type:
                texts_by_type[finding.__class__] = []
            texts_by_type[finding.__class__].append(
                FINDINGS[finding.__class__]
                .get("template", "")
                .format(
                    {
                        k: escape_markdown(
                            str(v) or "" if not isinstance(v, Finding) else v.__str__(),
                            version=2,
                        )
                        for k, v in finding.__dict__.items()
                    }
                )
            )
        message = EXECUTION.format(
            project=escape_markdown(execution.task.target.project.name, version=2),
            target=escape_markdown(execution.task.target.target, version=2),
            tool=escape_markdown(execution.configuration.tool.name, version=2),
            configuration=escape_markdown(execution.configuration.name, version=2),
            status=escape_markdown(execution.status, version=2),
            start=escape_markdown(
                execution.start.strftime(self.date_format), version=2
            ),
            end=escape_markdown(execution.end.strftime(self.date_format), version=2),
            executor=escape_markdown(execution.task.executor.username, version=2),
            findings="\n\n".join(
                [
                    HEADER.format(
                        icon=FINDINGS[finding_type].get("icon", ""),
                        title=finding_type.__name__,
                        details="\n\n".join(texts),
                    )
                    for finding_type, texts in texts_by_type.items()
                ]
            ),
        )
        for user in users:
            self._send_message(user.telegram_chat, message)

    def welcome_message(self, chat: TelegramChat) -> None:
        self._send_message(
            chat,
            escape_markdown(
                f"Welcome {chat.user.username}\! Your Rekono bot is ready", version=2
            ),
        )

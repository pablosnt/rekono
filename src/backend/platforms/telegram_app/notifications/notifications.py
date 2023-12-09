from typing import List

from executions.models import Execution
from findings.framework.models import Finding
from framework.platforms import BaseNotification
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.models import TelegramChat
from platforms.telegram_app.notifications.templates import EXECUTION, FINDINGS, HEADER
from users.models import User


class Telegram(BaseNotification, BaseTelegram):
    enable_field = "telegram_notifications"

    def is_available(self) -> bool:
        self.initialize()
        return bool(self.settings.secret and self.app and self.app.bot)

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
                        k: self._escape(
                            str(v) or "" if not isinstance(v, Finding) else v.__str__(),
                        )
                        for k, v in finding.__dict__.items()
                    }
                )
            )
        message = EXECUTION.format(
            project=self._escape(execution.task.target.project.name),
            target=self._escape(execution.task.target.target),
            tool=self._escape(execution.configuration.tool.name),
            configuration=self._escape(execution.configuration.name),
            status=self._escape(execution.status),
            start=self._escape(execution.start.strftime(self.date_format)),
            end=self._escape(execution.end.strftime(self.date_format)),
            executor=self._escape(execution.task.executor.username),
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
            f"Welcome *{self._escape(chat.user.username)}*\! Your Rekono bot is ready",
        )

    def logout_after_password_change_message(self, chat: TelegramChat) -> None:
        self._send_message(
            chat,
            "Your session in the Rekono bot has been closed after your password change. Please, execute /start to link it again",
        )

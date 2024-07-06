from typing import Any

from alerts.models import Alert
from django.forms.models import model_to_dict
from executions.models import Execution
from findings.framework.models import Finding
from framework.platforms import BaseNotification
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.notifications.templates import (
    ALERTS,
    EXECUTION,
    FINDINGS,
    HEADER,
)
from rekono.settings import CONFIG
from users.models import User


class Telegram(BaseNotification, BaseTelegram):
    enable_field = "telegram_notifications"

    def is_available(self) -> bool:
        self.initialize()
        return bool(self.settings.secret and self.app and self.app.bot)

    def _notify(self, users: list[Any], message: str) -> None:
        for user in users:
            if hasattr(user, "telegram_chat"):
                self._send_message(user.telegram_chat, message)

    def _notify_execution(
        self, users: list[User], execution: Execution, findings: list[Finding]
    ) -> None:
        texts_by_type: dict[Any, list[str]] = {}
        for finding in findings:
            if finding.__class__ not in texts_by_type:
                texts_by_type[finding.__class__] = []
            texts_by_type[finding.__class__].append(
                FINDINGS[finding.__class__]
                .get("template", "")
                .format(
                    **{
                        k: self._escape(
                            str(v) if not isinstance(v, Finding) else v.__str__(),
                        )
                        for k, v in model_to_dict(finding).items()
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
        self._notify(users, message)

    def _notify_alert(self, users: list[User], alert: Alert, finding: Finding) -> None:
        self._notify(
            users,
            HEADER.format(
                icon=FINDINGS[finding.__class__].get("icon", ""),
                title=ALERTS.get(alert.mode, "").format(
                    finding=finding.__class__.__name__.lower()
                ),
                details=FINDINGS[finding.__class__]
                .get("template", "")
                .format(
                    **{
                        k: self._escape(
                            str(v) if not isinstance(v, Finding) else v.__str__()
                        )
                        for k, v in model_to_dict(finding).items()
                    }
                ),
            ),
        )

    def welcome_message(self, user: User) -> None:
        self._notify_if_available(
            [user],
            f"Welcome *{self._escape(user.username)}*\! Your Rekono bot is ready",
        )

    def logout_after_password_change_message(self, user: User) -> None:
        self._notify_if_available(
            [user],
            "Your session in the Rekono bot has been closed after your password change. Please, execute /start to link it again",
        )

    def report_created(self, report: Any) -> None:
        self._notify_if_enabled(
            [report.user],
            f"{report.format.upper()} report with ID {report.id} from {f'project {report.project.name}' if report.project else (f'target {report.target.target}' if report.target else f'task {report.task.id}')} has been created and it's available to download it [here]({CONFIG.frontend_url}/#/projects/{report.get_project().id}/reports)",
        )

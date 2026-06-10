"""Telegram notification system for Rekono security events.

Provides Telegram-based notification delivery for security events including
execution results, alerts, and findings through Bot messaging.
"""

from typing import Any

from django.forms.models import model_to_dict

from alerts.enums import AlertItem
from alerts.models import Alert
from executions.models import Execution
from findings.framework.models import Finding
from framework.platforms import BaseNotification
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.notifications.templates import ALERT, ALERT_TRENDING_CVE, EXECUTION, FINDINGS, HEADER
from rekono.settings import CONFIG
from users.models import User


class Telegram(BaseNotification, BaseTelegram):
    """Telegram notification delivery system for security events.

    Handles delivery of security notifications through Telegram Bot messaging
    including execution results, alerts, and findings. Integrates with the
    base notification framework to provide real-time security event delivery.

    Attributes:
        enable_field (str): User profile field name to check if notifications are enabled.
    """

    enable_field = "telegram_notifications"

    def is_available(self) -> bool:
        """Check if Telegram notifications are available.

        Returns:
            bool: True if bot token is configured and application is ready.
        """
        return bool(self.settings and self.settings.secret and self.app and self.app.bot)

    def _notify(self, users: list[Any], message: str) -> None:
        """Send notification message to multiple users via Telegram.

        Args:
            users (list[Any]): List of users to notify.
            message (str): Message content to send.
        """
        for user in users:
            if hasattr(user, "telegram_chat"):
                self.send_message(user.telegram_chat, message)

    def _notify_execution(self, users: list[User], execution: Execution, findings: list[Finding]) -> None:
        """Send execution completion notification with findings summary.

        Formats and sends a comprehensive execution report including tool details,
        execution timing, and organized findings by type.

        Args:
            users (list[User]): Users to notify about the execution.
            execution (Execution): The completed security tool execution.
            findings (list[Finding]): List of security findings discovered.
        """
        texts_by_type: dict[Any, list[str]] = {}
        for finding in findings:
            if finding.created_from_user_input:
                continue
            if finding.__class__ not in texts_by_type:
                texts_by_type[finding.__class__] = []
            texts_by_type[finding.__class__].append(self._format_finding(finding))
        message = EXECUTION.format(
            project=self.escape(execution.task.target.project.name),
            target=self.escape(execution.task.target.target),
            tool=self.escape(execution.configuration.tool.name),
            configuration=self.escape(execution.configuration.name),
            status=self.escape(execution.status),
            start=self.escape(execution.start.strftime(self.date_format)),
            end=self.escape(execution.end.strftime(self.date_format)),
            executor=self.escape(execution.task.executor.username if execution.task.executor else "System"),
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
        """Send security alert notification for a specific finding.

        Args:
            users (list[User]): Users subscribed to the alert.
            alert (Alert): The alert configuration that triggered.
            finding (Finding): The security finding that triggered the alert.
        """
        self._notify(
            users,
            HEADER.format(
                icon=FINDINGS[finding.__class__].get("icon", ""),
                title=ALERT_TRENDING_CVE
                if alert.item == AlertItem.TRENDING_CVE
                else ALERT.format(finding=finding.__class__.__name__.lower()),
                details=self._format_finding(finding),
            ),
        )

    def _format_finding(self, finding: Finding) -> str:
        """Format a security finding for Telegram message display.

        Args:
            finding (Finding): The security finding to format.

        Returns:
            str: Formatted finding message with escaped content.
        """
        return (
            FINDINGS[finding.__class__]
            .get("template", "")
            .format(
                **{
                    k: self.escape(str(v) if not isinstance(v, Finding) else v.__str__())
                    for k, v in model_to_dict(finding).items()
                }
            )
        )

    def welcome_message(self, user: User) -> None:
        """Send welcome message to newly linked user.

        Args:
            user (User): The user who linked their Telegram account.
        """
        self._notify_if_available([user], f"Welcome *{self.escape(user.username)}*\! Your Rekono bot is ready")

    def logout_after_password_change_message(self, user: User) -> None:
        """Notify user of logout due to password change.

        Args:
            user (User): The user whose password was changed.
        """
        self._notify_if_available(
            [user], "Your session expired after your password change. Please, execute /start to link it again"
        )

    def report_created(self, report: Any) -> None:
        """Notify user when a security report is created.

        Args:
            report (Any): The generated security report instance.
        """
        report_target = (
            f"project {report.project.name}"
            if report.project
            else (f"target {report.target.target}" if report.target else f"task #{report.task.id}")
        )
        self._notify_if_enabled(
            [report.user],
            f"New {report.format.upper()} report for {report_target} is [available](({CONFIG.frontend_url}/projects/{report.parent_project.id}/reports)) to download",
        )

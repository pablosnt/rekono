"""Telegram notification system for Rekono security events.

Provides Telegram-based notification delivery for security events including
execution results, alerts, and findings through Bot messaging.
"""

from typing import Any

from django.forms.models import model_to_dict
from telegram.constants import MessageLimit

from alerts.enums import AlertItem
from alerts.models import Alert
from executions.models import Execution
from findings.framework.models import Finding
from framework.platforms import BaseNotification
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.notifications.templates import ALERT, ALERT_TRENDING_CVE, EXECUTION, FINDINGS, MESSAGE
from rekono.settings import CONFIG
from tasks.models import Task
from users.models import User


class Telegram(BaseNotification, BaseTelegram):
    """Telegram notification delivery for security events.

    Delivers execution reports, alerts, and findings to users over Telegram Bot
    messaging, splitting long reports across multiple messages to stay within
    Telegram's per-message length limit.

    Attributes:
        enable_field (str): User field name that toggles Telegram notifications.
        initial_findings_per_message (int): Findings per message when a report is
            split because it exceeds Telegram's length limit.
    """

    enable_field = "telegram_notifications"
    initial_findings_per_message = 10

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
        execution timing, and organized findings by type. The full report is sent as a
        single message, but if it exceeds Telegram's message length limit the findings are
        split into groups of `initial_findings_per_message`, keeping the execution details only in
        the first message. Any resulting message that is still too long is split in half
        again until every message fits within the limit.

        Args:
            users (list[User]): Users to notify about the execution.
            execution (Execution): The completed security tool execution.
            findings (list[Finding]): List of security findings discovered.
        """
        findings = [finding for finding in findings if not finding.created_from_user_input]
        message = self._execution_message(execution, findings)
        if len(message) <= MessageLimit.MAX_TEXT_LENGTH:
            self._notify(users, message)
        else:
            # The full report is too long, so send the findings in groups
            for index in range(0, len(findings), self.initial_findings_per_message):
                self._notify_execution_group(
                    users,
                    execution,
                    findings[index : index + self.initial_findings_per_message],
                    with_execution=index == 0,
                )

    def _notify_execution_group(
        self, users: list[User], execution: Execution, findings: list[Finding], with_execution: bool
    ) -> None:
        """Send a group of findings, splitting it in half if it exceeds the length limit.

        Args:
            users (list[User]): Users to notify about the execution.
            execution (Execution): The completed security tool execution.
            findings (list[Finding]): Findings included in this group.
            with_execution (bool): Whether to prepend the execution details to the message.
        """
        message = self._execution_message(execution, findings) if with_execution else self._format_findings(findings)
        if len(message) <= MessageLimit.MAX_TEXT_LENGTH:
            self._notify(users, message)
        elif len(findings) == 1:
            # A single finding can't be split further, so truncate it to fit within the limit
            self._notify(users, message[: MessageLimit.MAX_TEXT_LENGTH - 3] + "...")
        else:
            half = (len(findings) + 1) // 2
            self._notify_execution_group(users, execution, findings[:half], with_execution)
            self._notify_execution_group(users, execution, findings[half:], with_execution=False)

    def _execution_message(self, execution: Execution, findings: list[Finding]) -> str:
        """Build the execution report message with its findings summary.

        Args:
            execution (Execution): The completed security tool execution.
            findings (list[Finding]): Findings to include in this message.

        Returns:
            str: Formatted execution report ready to be sent.
        """
        return EXECUTION.format(
            project=self.escape(execution.task.target.project.name),
            target=self.escape(Task.get_target(execution.task.target, execution.task.target_port)),
            tool=self.escape(execution.configuration.tool.name),
            configuration=self.escape(execution.configuration.name),
            status=self.escape(execution.status),
            start=self.escape(execution.start.strftime(self.date_format)),
            end=self.escape(execution.end.strftime(self.date_format)),
            executor=self.escape(execution.task.executor.username if execution.task.executor else "System"),
            frontend_link=f"[Check scan in Rekono]({self.escape(f'{CONFIG.frontend_url}/projects/{execution.task.target.project.id}/scans/{execution.task.id}', entity_type='text_link')})",
            findings=self._format_findings(findings),
        )

    def _format_findings(self, findings: list[Finding]) -> str:
        """Format a group of findings organized by type for a Telegram message.

        Args:
            findings (list[Finding]): Findings to format.

        Returns:
            str: Findings summary grouped by type with the corresponding icons and titles.
        """
        texts_by_type: dict[Any, list[str]] = {}
        for finding in findings:
            texts_by_type.setdefault(finding.__class__, []).append(self._format_finding(finding))
        return "\n\n".join(
            MESSAGE.format(
                icon=FINDINGS[finding_type].get("icon", ""),
                title=finding_type.__name__,
                details="\n\n".join(texts),
            )
            for finding_type, texts in texts_by_type.items()
        )

    def _format_finding(self, finding: Finding) -> str:
        """Format a security finding for Telegram message display.

        Args:
            finding (Finding): The security finding to format.

        Returns:
            str: Formatted finding message with escaped content.
        """
        values = {}
        for field in model_to_dict(finding):
            value = getattr(finding, field)
            values[field] = self.escape(
                ", ".join(str(item) for item in value) if isinstance(value, list) else str(value)
            )
        return FINDINGS[finding.__class__].get("template", "").format(**values)

    def _notify_alert(self, users: list[User], alert: Alert, finding: Finding) -> None:
        """Send security alert notification for a specific finding.

        Args:
            users (list[User]): Users subscribed to the alert.
            alert (Alert): The alert configuration that triggered.
            finding (Finding): The security finding that triggered the alert.
        """
        self._notify(
            users,
            MESSAGE.format(
                icon=FINDINGS[finding.__class__].get("icon", ""),
                title=ALERT_TRENDING_CVE
                if alert.item == AlertItem.TRENDING_CVE
                else ALERT.format(finding=finding.__class__.__name__.lower()),
                details=self._format_finding(finding),
            ),
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

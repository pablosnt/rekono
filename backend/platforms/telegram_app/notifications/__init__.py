"""Notifications that Rekono sends through the Telegram bot."""

from typing import Any

from django.forms.models import model_to_dict
from telegram.constants import MessageLimit

from alerts.enums import AlertItem
from alerts.models import Alert
from executions.models import Execution
from findings.framework.models import Finding
from framework.platforms import BaseNotification
from platforms.telegram_app.framework import BaseTelegram
from platforms.telegram_app.notifications.templates import (
    ALERT,
    ALERT_TRENDING_CVE,
    EXECUTION,
    FINDINGS,
    MESSAGE,
    SUMMARY_ICON,
    SUMMARY_LINE,
)
from rekono.settings import CONFIG
from tasks.models import Task
from users.models import User


class Telegram(BaseNotification, BaseTelegram):
    """Notifications sent to the Telegram chats of the users that linked one.

    Attributes:
        enable_field: Field where the users say if they want to be notified.
        initial_findings_per_message: Findings that each message includes when a
          notification has to be split because it's too long for Telegram.
        findings_summary_threshold: Findings that an execution can report before
          its notification only includes how many of each type were found.
    """

    enable_field = "telegram_notifications"
    initial_findings_per_message = 10
    # Executions with more than these findings, are notified with a summary
    findings_summary_threshold = 50

    def is_available(self) -> bool:
        """Check if the platform can be used.

        Returns:
            Whether a bot token is configured and its client could be created.
        """
        return bool(self.settings and self.settings.secret and self.app and self.app.bot)

    def _notify(self, users: list[Any], message: str) -> None:
        """Send a message to the chats of the users that linked one.

        Args:
            users: Users to notify.
            message: Content of the message, written in Markdown.
        """
        for user in users:
            if hasattr(user, "telegram_chat"):
                self.send_message(user.telegram_chat, message)

    def _notify_execution(self, users: list[User], execution: Execution, findings: list[Finding]) -> None:
        """Notify the users that an execution finished, with what it discovered.

        An execution that discovered too many findings is notified with how many
        there are of each type instead, and a notification that doesn't fit in one
        Telegram message is split into as many as needed.

        Args:
            users: Users to notify.
            execution: Execution that finished.
            findings: Findings that the execution discovered.
        """
        # Findings entered manually by a user are not scan results, so they are left out of the notification
        findings = [finding for finding in findings if not finding.created_from_user_input]
        if len(findings) > self.findings_summary_threshold:
            # Too many findings, so send a summary notification
            self._notify(users, self._execution_message(execution, self._format_findings_summary(findings)))
            return
        message = self._execution_message(execution, self._format_findings(findings))
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
        """Notify a group of findings, splitting it again if it's still too long.

        Args:
            users: Users to notify.
            execution: Execution that discovered the findings.
            findings: Findings that this message includes.
            with_execution: Whether the message must include the execution data,
              which only the first message of a notification does.
        """
        message = (
            self._execution_message(execution, self._format_findings(findings))
            if with_execution
            else self._format_findings(findings)
        )
        if len(message) <= MessageLimit.MAX_TEXT_LENGTH:
            self._notify(users, message)
        elif len(findings) == 1:
            # A single finding can't be split further, so truncate it to fit within the limit
            self._notify(users, message[: MessageLimit.MAX_TEXT_LENGTH - 3] + "...")
        else:
            half = (len(findings) + 1) // 2
            self._notify_execution_group(users, execution, findings[:half], with_execution)
            self._notify_execution_group(users, execution, findings[half:], with_execution=False)

    def _execution_message(self, execution: Execution, findings: str) -> str:
        """Write the message that notifies an execution.

        Args:
            execution: Execution that finished.
            findings: Findings of the execution, already written as a text.

        Returns:
            The message, with what was scanned, how, and with a link to see the
            whole scan in Rekono.
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
            findings=findings,
        )

    def _format_findings_summary(self, findings: list[Finding]) -> str:
        """Write how many findings of each type an execution discovered.

        Args:
            findings: Findings to count.

        Returns:
            One line per finding type, with how many of them were discovered.
        """
        counts: dict[Any, int] = {}
        for finding in findings:
            counts[finding.__class__] = counts.get(finding.__class__, 0) + 1
        return MESSAGE.format(
            icon=SUMMARY_ICON,
            title=f"{len(findings)} findings detected",
            details="\n".join(
                SUMMARY_LINE.format(
                    icon=FINDINGS[finding_type].get("icon", ""), title=finding_type.__name__, count=count
                )
                for finding_type, count in counts.items()
                if count > 0
            ),
        )

    def _format_findings(self, findings: list[Finding]) -> str:
        """Write a group of findings as a text, grouped by their type.

        Args:
            findings: Findings to write.

        Returns:
            The findings of each type, under the name of that type.
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
        """Write one finding as a text, following the template of its type.

        Args:
            finding: Finding to write.

        Returns:
            The finding data, escaped so Telegram doesn't read it as Markdown.
        """
        values = {}
        for field in model_to_dict(finding):
            value = getattr(finding, field)
            values[field] = self.escape(
                ", ".join(str(item) for item in value) if isinstance(value, list) else str(value)
            )
        return FINDINGS[finding.__class__].get("template", "").format(**values)

    def _notify_alert(self, users: list[User], alert: Alert, finding: Finding) -> None:
        """Notify the users subscribed to an alert that it has been triggered.

        Args:
            users: Users to notify.
            alert: Alert that was triggered.
            finding: Finding that triggered the alert.
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
        """Welcome a user that has just linked their chat.

        Args:
            user: User that linked their chat.
        """
        self._notify_if_available([user], f"Welcome *{self.escape(user.username)}*\! Your Rekono bot is ready")

    def logout_after_password_change_message(self, user: User) -> None:
        """Tell a user that they have to link their chat again.

        Args:
            user: User whose password changed, which unlinks their chat.
        """
        self._notify_if_available(
            [user], "Your session expired after your password change. Please, execute /start to link it again"
        )

    def report_created(self, report: Any) -> None:
        """Notify a user that the report that they asked for is ready.

        Args:
            report: Report that was generated.
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

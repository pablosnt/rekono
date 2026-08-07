"""Notifications that Rekono sends by email."""

import os
import threading
from functools import cached_property
from typing import Any

import certifi
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import get_template
from django.utils import timezone

from alerts.enums import AlertItem
from alerts.models import Alert
from executions.models import Execution
from findings.framework.models import Finding
from framework.platforms import BaseNotification
from platforms.email.models import SMTPSettings
from rekono.settings import CONFIG
from tasks.models import Task


class SMTP(BaseNotification):
    """Notifications sent by email to the users that want to receive them.

    The account emails, like the invitations and the verification codes, are sent
    to everybody, since they are needed to use Rekono at all.

    Attributes:
        enable_field: Field where the users say if they want to be notified.
        datetime_format: Format that the dates are written in.
        findings_summary_threshold: Findings that an execution can report before
          its notification only includes how many of each type were found.
    """

    enable_field = "email_notifications"
    datetime_format = "%Y-%m-%d %H:%M %Z"
    # Executions with more than these findings, are notified with a summary
    findings_summary_threshold = 200

    @property
    def settings(self) -> SMTPSettings:
        """The SMTP configuration, or None if it hasn't been created yet."""
        return SMTPSettings.objects.first()

    @cached_property
    def backend(self) -> EmailBackend:
        """The client that sends the emails, or None if SMTP isn't configured.

        The connection with the server is only opened when an email is sent.
        """
        return (
            EmailBackend(
                host=self.settings.host,
                port=self.settings.port,
                username=self.settings.username,
                password=self.settings.secret,
                use_tls=self.settings.tls,
                timeout=5,
            )
            if self.settings
            else None
        )

    def __init__(self) -> None:
        """Prepare the platform, trusting the certificate authorities of certifi."""
        super().__init__()
        # Without this, SMTP TLS handshakes fail on systems that lack a system CA bundle
        os.environ["SSL_CERT_FILE"] = certifi.where()

    def is_available(self) -> bool:
        """Check if the platform can be used.

        Returns:
            Whether a server is configured and it accepts a connection with the
            configured credentials. It's always false during the tests, so they
            never reach a real mail server.
        """
        # Host and port are required for EmailBackend to attempt a connection at all, and
        # CONFIG.testing keeps tests from reaching out to a real mail server
        if not self.backend or not self.settings or not self.settings.host or not self.settings.port or CONFIG.testing:
            return False
        try:
            self.backend.open()
            self.backend.close()
            return True
        except Exception:
            return False

    def _send_messages(
        self, users: list[Any] | list[str], subject: str, template_path: str, data: dict[str, Any]
    ) -> None:
        """Send an email to the given recipients.

        A failure is logged instead of being propagated, so an email that can't be
        sent doesn't stop whatever was being done when it was sent.

        Args:
            users: Users to notify, or their email addresses, since the address
              verification is sent to an address that no user has yet.
            subject: Subject of the email.
            template_path: Template that the email content is built from.
            data: Data that the template needs.
        """
        if not self.is_available() or len(users) == 0:
            return
        # Callers may pass plain email addresses instead of user objects (see verify_email)
        if not isinstance(users[0], str):
            users = [u.email for u in users]
        sender = "Rekono <noreply@rekono.dev>"
        try:
            # Recipients in BCC not to leak their emails to other recipients
            message = EmailMultiAlternatives(
                subject,
                "",
                sender,
                to=[users[0]] if len(users) == 1 else None,
                bcc=users if len(users) > 1 else None,
            )
            template = get_template(template_path)
            # nosemgrep: python.flask.security.xss.audit.direct-use-of-jinja2.direct-use-of-jinja2
            message.attach_alternative(template.render({**data, "rekono_url": CONFIG.frontend_url}), "text/html")
            self.backend.send_messages([message])
        except Exception as ex:
            self.logger.error(f"[Mail] Error sending email message: {str(ex)}")

    def _notify(
        self, users: list[Any], subject: str, template: str, data: dict[str, Any], background: bool = True
    ) -> None:
        """Send a notification by email.

        Args:
            users: Users to notify.
            subject: Subject of the email.
            template: Template that the email content is built from.
            data: Data that the template needs.
            background: Whether the email must be sent in a thread, which isn't
              needed when the caller is already running in the background.
        """
        if background:
            threading.Thread(target=self._send_messages, args=(users, subject, template, data)).start()
        else:
            self._send_messages(users, subject, template, data)

    def _notify_execution(self, users: list[Any], execution: Execution, findings: list[Finding]) -> None:
        """Notify the users that an execution finished, with what it discovered.

        The findings are grouped by type, and an execution that discovered too many
        of them is notified with how many there are of each type instead, so the
        email stays readable.

        Args:
            users: Users to notify.
            execution: Execution that finished.
            findings: Findings that the execution discovered.
        """
        findings_by_class: dict[Any, list[Finding]] = {}
        for finding in findings:
            if finding.created_from_user_input:
                continue
            if finding.__class__.__name__ not in findings_by_class:
                findings_by_class[finding.__class__.__name__] = []
            findings_by_class[finding.__class__.__name__].append(finding)
        total = sum(len(items) for items in findings_by_class.values())
        self._notify(
            users,
            f"{execution.configuration.tool.name} scan completed",
            "execution_notification.html",
            {
                "execution": execution,
                "target": Task.get_target(execution.task.target, execution.task.target_port),
                **(
                    {
                        "summary_counts": [
                            {"title": finding_type, "count": len(findings)}
                            for finding_type, findings in findings_by_class.items()
                            if len(findings) > 0
                        ]
                    }
                    if total > self.findings_summary_threshold
                    else {k.lower(): v for k, v in findings_by_class.items()}
                ),
            },
            # Already running in the findings queue, so a thread of its own would only
            # detach the email from the job that must report its failure
            background=False,
        )

    def _notify_alert(self, users: list[Any], alert: Alert, finding: Finding) -> None:
        """Notify the users subscribed to an alert that it has been triggered.

        Args:
            users: Users to notify.
            alert: Alert that was triggered.
            finding: Finding that triggered the alert.
        """
        alert = (
            f"{finding.cve} is trending"
            if alert.item == AlertItem.TRENDING_CVE
            else f"new {finding.__class__.__name__.lower().replace('osint', 'OSINT')} detected"
        )
        self._notify(
            users,
            f"Alert triggered: {alert}",
            "alert_notification.html",
            {"alert": alert, "finding": finding, "finding_type": finding.__class__.__name__},
            # Already running in the findings queue, so a thread of its own would only
            # detach the email from the job that must report its failure
            background=False,
        )

    def invite_user(self, user: Any, otp: str) -> None:
        """Invite a user to Rekono, with the code that they need to claim the account.

        Args:
            user: User that was invited.
            otp: Code that the user needs to set their password.
        """
        self._notify_if_available(
            [user], "You have been invited to Rekono", "user_invitation.html", {"user": user, "user_otp": otp}
        )

    def reset_password(self, user: Any, otp: str) -> None:
        """Send the code that a user needs to reset their password.

        Args:
            user: User that asked to reset their password.
            otp: Code that the user needs to set the new password.
        """
        self._notify_if_available(
            [user], "Reset your password", "user_password_reset.html", {"user": user, "user_otp": otp}
        )

    def verify_email(self, user: Any, otp: str) -> None:
        """Send the code that verifies the new email address of a user.

        The code is sent to the new address, so only somebody who can read it is
        able to complete the change.

        Args:
            user: User that asked to change their email address.
            otp: Code that the user needs to confirm the new address.
        """
        self._notify_if_available(
            [user.pending_email],
            "Verify your email address",
            "user_email_verification.html",
            {"user": user, "user_otp": otp},
        )

    def email_change_notification(self, user: Any) -> None:
        """Warn a user that their email address is being changed.

        The warning goes to the current address, so the user can react if it wasn't
        them who asked for the change.

        Args:
            user: User whose email address is being changed.
        """
        self._notify_if_available(
            [user],
            "Your account email is being changed",
            "user_email_change_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def mfa(self, user: Any, otp: str) -> None:
        """Send the code that a user needs to complete their login.

        Args:
            user: User that is logging in.
            otp: Code that the user needs as their second factor.
        """
        self._notify_if_available([user], "Your verification code", "user_mfa.html", {"user": user, "user_otp": otp})

    def enable_user_account(self, user: Any, otp: str) -> None:
        """Send the code that a user needs to use their account again.

        Args:
            user: User whose account was enabled again.
            otp: Code that the user needs to set their password.
        """
        self._notify_if_available(
            [user], "Welcome back to Rekono", "user_enable_account.html", {"user": user, "user_otp": otp}
        )

    def login_notification(self, user: Any) -> None:
        """Warn a user that somebody logged into their account.

        Args:
            user: User that logged in.
        """
        self._notify_if_available(
            [user],
            "New sign-in to your account",
            "user_login_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def telegram_linked_notification(self, user: Any) -> None:
        """Warn a user that their account was linked to a Telegram chat.

        Args:
            user: User that linked their account.
        """
        self._notify_if_available(
            [user],
            "Telegram bot linked to your account",
            "user_telegram_linked_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def report_created(self, report: Any) -> None:
        """Notify a user that the report that they asked for is ready.

        This is the only email of this platform that isn't about the account, so
        it's the only one that the users can choose not to receive.

        Args:
            report: Report that was generated.
        """
        self._notify_if_enabled(
            [report.user], f"Your {report.format.upper()} report is ready", "report_created.html", {"report": report}
        )

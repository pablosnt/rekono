"""Email notification implementation using SMTP protocol.

Provides comprehensive email notification functionality for Rekono's security testing
platform. Handles all email-based notifications including security findings, alerts,
user management events, and system notifications through secure SMTP connections.
"""

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
    """SMTP-based email notification system for Rekono platform.

    Implements comprehensive email notification functionality using SMTP protocol
    for delivering security findings, alerts, user management notifications, and
    system events. Provides secure email delivery with TLS support and HTML
    template-based formatting.

    Security Features:
        - Secure SMTP connections with TLS encryption
        - Certificate validation using trusted certificate authorities
        - Encrypted credential storage and secure connection management

    Notification Categories:
        - Security findings and execution completion notifications
        - Alert notifications for new discoveries and trending threats
        - User account management (invitations, password resets, MFA)
        - System notifications and report generation alerts

    Attributes:
        enable_field (str): User preference field for email notification control
        datetime_format (str): Standard datetime format for email content
        findings_summary_threshold (int): Finding count above which an execution
                                          notification switches from detailed
                                          finding lists to per-type counts
    """

    enable_field = "email_notifications"
    datetime_format = "%Y-%m-%d %H:%M %Z"
    # Executions with more than these findings, are notified with a summary
    findings_summary_threshold = 200

    @property
    def settings(self) -> SMTPSettings:
        """Get SMTP server configuration settings from database.

        Returns:
            SMTPSettings: SMTP configuration instance or None if not configured.
        """
        return SMTPSettings.objects.first()

    @cached_property
    def backend(self) -> EmailBackend:
        """Build the SMTP email backend from the stored configuration.

        Configures Django's EmailBackend with the host, port, credentials, TLS flag,
        and a 5 second connection timeout read from SMTPSettings. The connection itself
        is only opened later, when a message is sent or when is_available tests it.

        Returns:
            EmailBackend: Configured SMTP backend instance, or None if SMTP is not
                          configured at all (SMTPSettings.objects.first() is None).
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
        """Initialize SMTP notification system with secure certificate configuration.

        Sets up the SMTP notification system with trusted SSL certificate validation
        using the certifi package to ensure secure connections to SMTP servers.
        """
        super().__init__()
        # Without this, SMTP TLS handshakes fail on systems that lack a system CA bundle
        os.environ["SSL_CERT_FILE"] = certifi.where()

    def is_available(self) -> bool:
        """Check if SMTP email service is available and properly configured.

        Requires a stored SMTPSettings row with both a host and a port before attempting
        anything else. Availability is always False while CONFIG.testing is set, so unit
        and integration tests never open a real SMTP connection. Otherwise, it opens and
        immediately closes a connection to the configured mail server to confirm it is
        reachable and the credentials are accepted.

        Returns:
            bool: True if SMTP is configured and the mail server accepted the
                  connection, False otherwise.
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
        """Render an HTML template and send it as an email to the given recipients.

        Accepts either user objects or raw email address strings, since some notifications
        (email address verification) target a pending address with no user lookup of its
        own. Recipients are placed in BCC when there is more than one, so they can't see
        each other's addresses; a single recipient is addressed directly instead. Does
        nothing if SMTP is unavailable or no users were given, and logs rather than raises
        if rendering or sending the message fails.

        Args:
            users (list[Any] | list[str]): User objects with an email attribute, or raw
                                           email address strings.
            subject (str): Email subject line.
            template_path (str): Filename of the HTML template to render.
            data (dict[str, Any]): Template context data for rendering.
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
        """Send notification emails to users with optional background processing.

        Core notification method that handles email delivery with support for
        background processing to avoid blocking operations. Delegates to
        _send_messages for actual email transmission.

        Args:
            users (list[Any]): List of user objects to notify
            subject (str): Email subject line
            template (str): HTML template filename for email content
            data (dict[str, Any]): Template context data for rendering
            background (bool): Whether to send emails in background thread (default True)
        """
        if background:
            threading.Thread(target=self._send_messages, args=(users, subject, template, data)).start()
        else:
            self._send_messages(users, subject, template, data)

    def _notify_execution(self, users: list[Any], execution: Execution, findings: list[Finding]) -> None:
        """Send an execution completion notification summarizing its findings.

        Groups findings by class name, skipping any created from user input rather than
        discovered by the tool itself. When the total exceeds findings_summary_threshold,
        the template receives a per-type count instead of the full finding lists, keeping
        the email a reasonable size for executions with very large result sets.

        Args:
            users (list[Any]): Users to notify about the execution.
            execution (Execution): The completed execution instance.
            findings (list[Finding]): Findings discovered by the execution.
        """
        findings_by_class: dict[Any, list[Finding]] = {}
        for finding in findings:
            if finding.created_from_user_input:
                continue
            if finding.__class__.__name__ not in findings_by_class:
                findings_by_class[finding.__class__.__name__] = []
            findings_by_class[finding.__class__.__name__].append(finding)
        total = sum(len(items) for items in findings_by_class.values())
        # This is called from findings queue which is already asynchronous
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
            background=False,
        )

    def _notify_alert(self, users: list[Any], alert: Alert, finding: Finding) -> None:
        """Send an alert notification for a finding that matched an alert rule.

        The subject reads "<cve> is trending" for trending CVE alerts, or
        "new <finding type> detected" for every other alert item, with "osint"
        cased as "OSINT".

        Args:
            users (list[Any]): Users subscribed to the alert.
            alert (Alert): The triggered alert configuration.
            finding (Finding): The finding that triggered the alert.
        """
        # This is called from findings queue which is already asynchronous
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
            background=False,
        )

    def invite_user(self, user: Any, otp: str) -> None:
        """Send a welcome email with the one-time password needed to claim the account.

        Args:
            user (Any): The invited user.
            otp (str): One-time password for account activation.
        """
        self._notify_if_available(
            [user], "You have been invited to Rekono", "user_invitation.html", {"user": user, "user_otp": otp}
        )

    def reset_password(self, user: Any, otp: str) -> None:
        """Send a password reset email with the one-time password needed to reset it.

        Args:
            user (Any): The user requesting the password reset.
            otp (str): One-time password for the reset.
        """
        self._notify_if_available(
            [user], "Reset your password", "user_password_reset.html", {"user": user, "user_otp": otp}
        )

    def verify_email(self, user: Any, otp: str) -> None:
        """Send an email verification message to a pending email address.

        Delivers a verification link with a one-time password to the new address a user
        wants to switch to. The message is sent to the pending address, not the current
        one, so only someone with access to the new inbox can confirm the change.

        Args:
            user (Any): The user requesting the email change.
            otp (str): One-time password for confirming the new email address.
        """
        self._notify_if_available(
            [user.pending_email],
            "Verify your email address",
            "user_email_verification.html",
            {"user": user, "user_otp": otp},
        )

    def email_change_notification(self, user: Any) -> None:
        """Send a security notice about a requested email change to the current address.

        Warns the current email address that a change to a different address was
        requested, so the user can react (for example by resetting their password) if
        the request was not made by them.

        Args:
            user (Any): The user whose email change was requested.
        """
        self._notify_if_available(
            [user],
            "Your account email is being changed",
            "user_email_change_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def mfa(self, user: Any, otp: str) -> None:
        """Send the one-time password used as the second factor during login.

        Args:
            user (Any): The user logging in.
            otp (str): One-time password for multi-factor authentication.
        """
        self._notify_if_available([user], "Your verification code", "user_mfa.html", {"user": user, "user_otp": otp})

    def enable_user_account(self, user: Any, otp: str) -> None:
        """Send a re-enablement email with the one-time password needed to access the account again.

        Args:
            user (Any): The user whose account was enabled.
            otp (str): One-time password for account activation.
        """
        self._notify_if_available(
            [user], "Welcome back to Rekono", "user_enable_account.html", {"user": user, "user_otp": otp}
        )

    def login_notification(self, user: Any) -> None:
        """Send a security notice about a new sign-in to the account, with a timestamp.

        Args:
            user (Any): The user who signed in.
        """
        self._notify_if_available(
            [user],
            "New sign-in to your account",
            "user_login_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def telegram_linked_notification(self, user: Any) -> None:
        """Send a confirmation email that the account was linked to a Telegram chat, with a timestamp.

        Args:
            user (Any): The user who linked their Telegram account.
        """
        self._notify_if_available(
            [user],
            "Telegram bot linked to your account",
            "user_telegram_linked_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def report_created(self, report: Any) -> None:
        """Send a notification that a requested report has finished generating.

        Uses _notify_if_enabled rather than _notify_if_available, so unlike the account
        and security emails above, this respects the recipient's email notification
        preference and is skipped for users who disabled it.

        Args:
            report (Any): The generated report, providing format and owning user.
        """
        self._notify_if_enabled(
            [report.user], f"Your {report.format.upper()} report is ready", "report_created.html", {"report": report}
        )

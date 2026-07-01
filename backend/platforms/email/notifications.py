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
    """

    enable_field = "email_notifications"
    datetime_format = "%Y-%m-%d %H:%M %Z"

    @property
    def settings(self) -> SMTPSettings:
        """Get SMTP server configuration settings from database.

        Returns:
            SMTPSettings: SMTP configuration instance or None if not configured.
        """
        return SMTPSettings.objects.first()

    @cached_property
    def backend(self) -> EmailBackend:
        """Create and configure SMTP email backend.

        Initializes Django's EmailBackend with SMTP settings from the database
        configuration. Creates a secure connection with TLS encryption and
        timeout handling for reliable email delivery.

        Returns:
            EmailBackend: Configured SMTP backend instance or None if settings unavailable
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

        Validates SMTP configuration and tests connection to the mail server
        by attempting to open and close a connection. Ensures all required
        settings are present before testing connectivity.

        Returns:
            bool: True if SMTP service is available and functional, False otherwise
        """
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
        """Send HTML email messages to specified users using configured template.

        Renders HTML email template with provided data and sends formatted emails
        to all specified users. Includes error handling and logging for failed
        email delivery attempts.

        Args:
            users (list[Any]): List of user objects with email addresses
            subject (str): Email subject line
            template_path (str): Path to HTML email template
            data (dict[str, Any]): Template context data for rendering
        """
        if not self.is_available() or len(users) == 0:
            return
        if not isinstance(users[0], str):
            users = [u.email for u in users]
        sender = "Rekono <noreply@rekono.com>"
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
        """Send execution completion notification with findings summary.

        Notifies users about completed security tool execution with organized
        findings grouped by type. Provides comprehensive execution results
        and discovered security findings in formatted email.

        Args:
            users (list[Any]): List of users to notify about execution completion
            execution (Execution): The completed execution instance
            findings (list[Finding]): List of security findings discovered
        """
        findings_by_class: dict[Any, list[Finding]] = {}
        for finding in findings:
            if finding.created_from_user_input:
                continue
            if finding.__class__.__name__.lower() not in findings_by_class:
                findings_by_class[finding.__class__.__name__.lower()] = []
            findings_by_class[finding.__class__.__name__.lower()].append(finding)
        # This is called from findings queue which is already asynchronous
        self._notify(
            users,
            f"{execution.configuration.tool.name} scan completed",
            "execution_notification.html",
            {"execution": execution, **findings_by_class},
            background=False,
        )

    def _notify_alert(self, users: list[Any], alert: Alert, finding: Finding) -> None:
        """Send alert notification for security finding matching alert criteria.

        Notifies users about security findings that match configured alert rules.
        Provides contextual subject lines based on alert mode (NEW, FILTER, MONITOR)
        and includes both alert configuration and finding details.

        Args:
            users (list[Any]): List of users subscribed to the alert
            alert (Alert): The triggered alert configuration
            finding (Finding): The security finding that triggered the alert
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
        """Send user invitation email with account setup instructions.

        Sends welcome email to newly invited users with account activation
        instructions and one-time password for initial account setup.

        Args:
            user (Any): The invited user object
            otp (str): One-time password for account activation
        """
        self._notify_if_available(
            [user], "You have been invited to Rekono", "user_invitation.html", {"user": user, "user_otp": otp}
        )

    def reset_password(self, user: Any, otp: str) -> None:
        """Send password reset email with secure reset instructions.

        Sends password reset email containing secure reset link and one-time
        password for user authentication during password reset process.

        Args:
            user (Any): The user requesting password reset
            otp (str): One-time password for secure password reset
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
        """Send multi-factor authentication email with one-time password.

        Delivers MFA token via email for two-factor authentication during
        login process, providing secure second factor verification.

        Args:
            user (Any): The user requesting MFA token
            otp (str): One-time password for multi-factor authentication
        """
        self._notify_if_available([user], "Your verification code", "user_mfa.html", {"user": user, "user_otp": otp})

    def enable_user_account(self, user: Any, otp: str) -> None:
        """Send account enablement notification with activation instructions.

        Notifies users that their account has been enabled and provides
        activation instructions with one-time password for account access.

        Args:
            user (Any): The user whose account was enabled
            otp (str): One-time password for account activation
        """
        self._notify_if_available(
            [user], "Welcome back to Rekono", "user_enable_account.html", {"user": user, "user_otp": otp}
        )

    def login_notification(self, user: Any) -> None:
        """Send security notification for new account login.

        Sends security alert email notifying users about new login activity
        on their account with timestamp information for security monitoring.

        Args:
            user (Any): The user who logged into the account
        """
        self._notify_if_available(
            [user],
            "New sign-in to your account",
            "user_login_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def telegram_linked_notification(self, user: Any) -> None:
        """Send confirmation email for Telegram bot integration setup.

        Notifies users about successful Telegram bot account linking with
        welcome message and timestamp for integration confirmation.

        Args:
            user (Any): The user who linked their Telegram account
        """
        self._notify_if_available(
            [user],
            "Telegram bot linked to your account",
            "user_telegram_linked_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def report_created(self, report: Any) -> None:
        """Send notification when security report generation is completed.

        Notifies users when their requested security reports have been generated
        and are ready for download, including report format and access information.

        Args:
            report (Any): The generated report object with format and download details
        """
        self._notify_if_enabled(
            [report.user], f"Your {report.format.upper()} report is ready", "report_created.html", {"report": report}
        )

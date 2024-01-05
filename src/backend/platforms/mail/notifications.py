import logging
import os
import threading
from typing import Any, Dict, List

import certifi
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import get_template
from django.utils import timezone
from executions.models import Execution
from findings.framework.models import Finding
from framework.platforms import BaseNotification
from platforms.mail.models import SMTPSettings
from rekono.settings import CONFIG

logger = logging.getLogger()


class SMTP(BaseNotification):
    enable_field = "email_notifications"

    def __init__(self) -> None:
        self.settings = SMTPSettings.objects.first()
        self.backend = (
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
        self.datetime_format = "%Y-%m-%d %H:%M %Z"
        # The trusted certificates must be defined
        os.environ["SSL_CERT_FILE"] = certifi.where()

    def is_available(self) -> bool:
        if (
            not self.settings
            or not self.settings.host
            or not self.settings.port
            or CONFIG.testing
        ):
            return False
        try:
            self.backend.open()
            self.backend.close()
            return True
        except Exception:
            return False

    def _send_messages_in_background(
        self, users: List[Any], subject: str, template: str, data: Dict[str, Any]
    ) -> None:
        threading.Thread(
            target=self._send_messages, args=(users, subject, template, data)
        ).start()

    def _send_messages(
        self, users: List[Any], subject: str, template_path: str, data: Dict[str, Any]
    ) -> None:
        if not self.is_available():
            return
        try:
            message = EmailMultiAlternatives(
                subject, "", "Rekono <noreply@rekono.com>", [u.email for u in users]
            )
            template = get_template(template_path)
            # nosemgrep: python.flask.security.xss.audit.direct-use-of-jinja2.direct-use-of-jinja2
            message.attach_alternative(
                template.render(**{**data, "rekono_url": CONFIG.frontend_url}),
                "text/html",
            )
            self.backend.send_messages([message])
        except Exception:
            logger.error("[Mail] Error sending email message")

    def _notify_execution(
        self, users: List[Any], execution: Execution, findings: List[Finding]
    ) -> None:
        findings_by_class: Dict[Any, List[Finding]] = {}
        for finding in findings:
            if findings.__class__.__name__.lower() not in findings_by_class:
                findings_by_class[findings.__class__.__name__.lower()] = []
            findings_by_class[findings.__class__.__name__.lower()].append(finding)
        self._send_messages(
            users,
            f"[Rekono] {execution.configuration.tool.name} execution completed",
            "execution_notification.html",
            {
                "execution": execution,
                **findings_by_class,
            },
        )

    def invite_user(self, user: Any, otp: str) -> None:
        self._send_messages_in_background(
            [user],
            "Welcome to Rekono",
            "user_invitation.html",
            {"user": user, "user_otp": otp},
        )

    def reset_password(self, user: Any, otp: str) -> None:
        self._send_messages_in_background(
            [user],
            "Reset Rekono password",
            "user_password_reset.html",
            {"user": user, "user_otp": otp},
        )

    def enable_user_account(self, user: Any, otp: str) -> None:
        self._send_messages_in_background(
            [user],
            "Rekono user enabled",
            "user_enable_account.html",
            {"user": user, "user_otp": otp},
        )

    def login_notification(self, user: Any) -> None:
        self._send_messages_in_background(
            [user],
            "New login in your Rekono account",
            "user_login_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def telegram_linked_notification(self, user: Any) -> None:
        self._send_messages_in_background(
            [user],
            "Welcome to Rekono Bot",
            "user_telegram_linked_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def report_created(self, report: Any) -> None:
        if self.is_enabled(report.user):
            self._send_messages(
                [report.user],
                f"{report.format.upper()} report is ready",
                "report_created.html",
                {"report": report},
            )

import logging
import os
import threading
from typing import Any

import certifi
from alerts.enums import AlertMode
from alerts.models import Alert
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
            not self.backend
            or not self.settings
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

    def _send_messages(
        self, users: list[Any], subject: str, template_path: str, data: dict[str, Any]
    ) -> None:
        if not self.backend or not self.is_available():
            return
        try:
            message = EmailMultiAlternatives(
                subject, "", "Rekono <noreply@rekono.com>", [u.email for u in users]
            )
            template = get_template(template_path)
            message.attach_alternative(
                # nosemgrep: python.flask.security.xss.audit.direct-use-of-jinja2.direct-use-of-jinja2
                template.render({**data, "rekono_url": CONFIG.frontend_url}),
                "text/html",
            )
            self.backend.send_messages([message])
        except Exception as ex:
            logger.error(f"[Mail] Error sending email message: {str(ex)}")

    def _notify(
        self,
        users: list[Any],
        subject: str,
        template: str,
        data: dict[str, Any],
        background: bool = True,
    ) -> None:
        if background:
            threading.Thread(
                target=self._send_messages, args=(users, subject, template, data)
            ).start()
        else:
            self._send_messages(users, subject, template, data)

    def _notify_execution(
        self, users: list[Any], execution: Execution, findings: list[Finding]
    ) -> None:
        findings_by_class: dict[Any, list[Finding]] = {}
        for finding in findings:
            if findings.__class__.__name__.lower() not in findings_by_class:
                findings_by_class[findings.__class__.__name__.lower()] = []
            findings_by_class[findings.__class__.__name__.lower()].append(finding)
        self._notify(
            users,
            f"[Rekono] {execution.configuration.tool.name} execution completed",
            "execution_notification.html",
            {
                "execution": execution,
                **findings_by_class,
            },
            background=False,
        )

    def _notify_alert(self, users: list[Any], alert: Alert, finding: Finding) -> None:
        subjects = {
            AlertMode.NEW: f"New {finding.__class__.__name__.lower()} detected",
            AlertMode.FILTER.value: f"New {finding.__class__.__name__.lower()} matches alert criterion",
            AlertMode.MONITOR.value: "New trending CVE",
        }
        self._notify(
            users,
            f"[Rekono] {subjects[alert.mode]}",
            "alert_notification.html",
            {"alert": alert, "finding": finding},
            background=False,
        )

    def invite_user(self, user: Any, otp: str) -> None:
        self._notify_if_available(
            [user],
            "Welcome to Rekono",
            "user_invitation.html",
            {"user": user, "user_otp": otp},
        )

    def reset_password(self, user: Any, otp: str) -> None:
        self._notify_if_available(
            [user],
            "Reset Rekono password",
            "user_password_reset.html",
            {"user": user, "user_otp": otp},
        )

    def mfa(self, user: Any, otp: str) -> None:
        self._notify_if_available(
            [user],
            "[Rekono] One Time Password",
            "user_mfa.html",
            {"user": user, "user_otp": otp},
        )

    def enable_user_account(self, user: Any, otp: str) -> None:
        self._notify_if_available(
            [user],
            "Rekono user enabled",
            "user_enable_account.html",
            {"user": user, "user_otp": otp},
        )

    def login_notification(self, user: Any) -> None:
        self._notify_if_available(
            [user],
            "New login in your Rekono account",
            "user_login_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def telegram_linked_notification(self, user: Any) -> None:
        self._notify_if_available(
            [user],
            "Welcome to Rekono Bot",
            "user_telegram_linked_notification.html",
            {"time": timezone.now().strftime(self.datetime_format)},
        )

    def report_created(self, report: Any) -> None:
        self._notify_if_enabled(
            [report.user],
            f"{report.format.upper()} report is ready",
            "report_created.html",
            {"report": report},
        )

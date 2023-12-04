import logging
import threading
from typing import Any, Dict, List

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
    enable_field = "email_notification"

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
        self.datetime_format = "%Y-%m-%d %H:%M"

    def is_available(self) -> bool:
        if not self.settings or not self.settings.host or not self.settings.port:
            return False
        try:
            self.backend.open()
            self.backend.close()
            return True
        except:
            return False

    def _send_messages_in_background(
        self, users: List[Any], subject: str, template: str, data: Dict[str, Any]
    ) -> None:
        threading.Thread(
            target=self._send_messages, args=(users, subject, template, data)
        )

    def _send_messages(
        self, users: List[Any], subject: str, template: str, data: Dict[str, Any]
    ) -> None:
        if self.is_available():
            try:
                message = EmailMultiAlternatives(
                    subject, "", "Rekono <noreply@rekono.com>", [u.email for u in users]
                )
                template = get_template(template)
                data["rekono_url"] = CONFIG.frontend_url
                # nosemgrep: python.flask.security.xss.audit.direct-use-of-jinja2.direct-use-of-jinja2
                message.attach_alternative(template.render(data), "text/html")
                self.backend.send_messages([message])
            except Exception:
                logger.error("[Mail] Error sending email message")

    def _notify_execution(
        self, users: List[Any], execution: Execution, findings: List[Finding]
    ) -> None:
        findings_by_class = {}
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

    def invite_user(self, user: Any) -> None:
        self._send_messages_in_background(
            [user], "Welcome to Rekono", "user_invitation.html", {"user": user}
        )

    def reset_password(self, user: Any) -> None:
        self._send_messages_in_background(
            [user], "Reset Rekono password", "user_password_reset.html", {"user": user}
        )

    def enable_user_account(self, user: Any) -> None:
        self._send_messages_in_background(
            [user], "Rekono user enabled", "user_enable_account.html", {"user": user}
        )

    def login_notification(self, user: Any) -> None:
        self._send_messages_in_background(
            [user],
            "New login in your Rekono account",
            "user_login_notification.html",
            data={"time": timezone.now().strftime(self.datetime_format)},
        )

    def telegram_linked_notification(self, user: Any) -> None:
        self._send_messages_in_background(
            [user],
            "Welcome to Rekono Bot",
            "user_telegram_linked_notification.html",
            data={"time": timezone.now().strftime(self.datetime_format)},
        )

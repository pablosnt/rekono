import logging
from typing import Any, Callable
from urllib.parse import urlparse

import requests
from alerts.models import Alert
from executions.models import Execution
from findings.framework.models import Finding
from integrations.models import Integration
from requests.adapters import HTTPAdapter, Retry
from users.enums import Notification

logger = logging.getLogger()


class BasePlatform:
    def is_available(self) -> bool:
        return True


class BaseIntegration(BasePlatform):
    url = ""

    def __init__(self) -> None:
        self.session = self._create_session(self.url)
        self.integration = Integration.objects.get(key=self.__class__.__name__.lower())

    def _create_session(self, url: str) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=10,
            backoff_factor=1,
            status_forcelist=[403, 429, 500, 502, 503, 504, 599],
        )
        session.mount(f"{urlparse(url).scheme}://", HTTPAdapter(max_retries=retries))
        return session

    def _request(
        self, method: Callable, url: str, json: bool = True, **kwargs: Any
    ) -> Any:
        try:
            response = method(url, **kwargs)
        except requests.exceptions.ConnectionError:
            response = method(url, **kwargs)
        logger.info(
            f"[{self.__class__.__name__}] {method.__name__.upper()} {urlparse(url).path} > HTTP {response.status_code}"
        )
        response.raise_for_status()
        return response.json() if json else response

    def is_enabled(self) -> bool:
        return self.integration.enabled if self.integration else False

    def _process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        pass

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        if not self.is_enabled():
            return
        self._process_findings(execution, findings)


class BaseNotification(BasePlatform):
    enable_field = ""

    def is_enabled(self, user: Any) -> bool:
        return getattr(user, self.enable_field)

    def _notify(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        pass

    def _notify_if_available(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        if self.is_available():
            self._notify(users, *args, **kwargs)

    def _notify_if_enabled(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        if self.is_available():
            for user in users:
                if self.is_enabled(user):
                    self._notify([user], *args, **kwargs)

    def _get_users_to_notify_execution(self, execution: Execution) -> list[Any]:
        users = set()
        if (
            execution.task.executor.notification_scope != Notification.DISABLED
            and getattr(execution.task.executor, self.enable_field)
        ):
            users.add(execution.task.executor)
        users.update(
            execution.task.target.project.members.filter(
                **{
                    self.enable_field: True,
                    "notification_scope": Notification.ALL_EXECUTIONS,
                }
            ).exclude(id=execution.task.executor.id)
        )
        return list(users)

    def _get_users_to_notify_alert(self, alert: Alert) -> list[Any]:
        return alert.subscribers.filter(**{self.enable_field: True}).all()

    def _notify_execution(
        self, users: list[Any], execution: Execution, findings: list[Finding]
    ) -> None:
        pass

    def _notify_alert(self, users: list[Any], alert: Alert, finding: Finding) -> None:
        pass

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        if not self.is_available():
            return
        users = self._get_users_to_notify_execution(execution)
        self._notify_execution(users, execution, findings)

    def process_alert(self, alert: Alert, finding: Finding) -> None:
        if not self.is_available():
            return
        self._notify_alert(
            alert.subscribers.filter(**{self.enable_field: True}).all(), alert, finding
        )

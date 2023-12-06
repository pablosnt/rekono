import logging
from typing import Any, List
from urllib.parse import urlparse

import requests
from executions.models import Execution
from findings.framework.models import Finding
from requests.adapters import HTTPAdapter, Retry
from users.enums import Notification

logger = logging.getLogger()


class BasePlatform:
    def is_available(self) -> bool:
        return True

    def process_findings(self, execution: Execution, findings: List[Finding]) -> None:
        if not self.is_available():
            return


class BaseIntegration(BasePlatform):
    url = ""

    def __init__(self) -> None:
        self.session = self._create_session(self.url)

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
        self, method: callable, url: str, json: bool = True, **kwargs: Any
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


class BaseNotification(BasePlatform):
    enable_field = ""

    def _get_users_to_notify(self, execution: Execution) -> List[Any]:
        users = set()
        if (
            execution.task.executor.notification_scope != Notification.DISABLED
            and getattr(execution.task.executor, self.enable_field)
        ):
            users.add(execution.task.executor)
        search = {
            self.enable_field: True,
            "notification_scope": Notification.ALL_EXECUTIONS,
        }
        users.update(
            execution.task.target.project.members.filter(**search).exclude(
                id=execution.task.executor.id
            )
        )
        return users

    def _notify_execution(
        self, users: List[Any], execution: Execution, findings: List[Finding]
    ) -> None:
        pass

    def process_findings(self, execution: Execution, findings: List[Finding]) -> None:
        super().process_findings(execution, findings)
        users = self._get_users_to_notify(execution)
        self._notify_execution(users, execution, findings)

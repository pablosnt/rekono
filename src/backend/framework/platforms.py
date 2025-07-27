from functools import cached_property
from typing import Any, Callable
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter, Retry

from alerts.models import Alert
from executions.models import Execution
from findings.framework.models import Finding
from framework.logging import LoggingEntity
from integrations.models import Integration
from users.enums import Notification


class BasePlatform(LoggingEntity):
    """Base class for platform integrations and notifications.

    This abstract base class provides common functionality for platform
    integrations and notification systems. It includes methods for checking
    availability and processing findings.
    """

    def is_enabled(self) -> bool:
        """Check if the platform is enabled.

        Returns:
            True if the platform is enabled, False otherwise.
        """
        return True

    def is_available(self) -> bool:
        """Check if the platform is available for use.

        Returns:
            True if the platform is available, False otherwise.
        """
        return True

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Process findings through this platform.

        Args:
            execution: The execution context.
            findings: List of findings to process.
        """
        pass


class BaseIntegration(BasePlatform):
    """Base class for external platform integrations.

    This abstract base class provides functionality for integrating with
    external platforms and APIs. It includes HTTP session management,
    retry logic, and finding processing capabilities.

    Attributes:
        url (str): Base URL for the integration API.
        finding_types (list): List of finding types this integration processes.
        run_per_execution (bool): Whether to run per execution or per finding.
    """

    url = ""
    finding_types = []  # If empty, all findings are processed
    run_per_execution = False

    @cached_property
    def integration(self) -> Integration:
        """Get the integration configuration.

        Returns:
            The Integration instance for this platform.
        """
        return Integration.objects.get(key=self.__class__.__name__.lower())

    @cached_property
    def session(self) -> requests.Session:
        """Get HTTP session with retry configuration.

        Returns:
            Configured requests.Session with retry logic.
        """
        session = requests.Session()
        session.mount(
            f"{urlparse(self.url).scheme}://",
            HTTPAdapter(
                max_retries=Retry(
                    total=10,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504, 599],
                )
            ),
        )
        return session

    def is_enabled(self) -> bool:
        """Check if the integration is enabled.

        Returns:
            True if the integration is enabled, False otherwise.
        """
        return self.integration.enabled if self.integration else False

    def _request(
        self,
        method: Callable,
        url: str,
        json: bool = True,
        trigger_exception: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Make HTTP request with retry logic and logging.

        Args:
            method: HTTP method function (GET, POST, etc.).
            url: URL to request.
            json: Whether to return JSON response.
            trigger_exception: Whether to raise exceptions on HTTP errors.
            **kwargs: Additional arguments for the request.

        Returns:
            Response data (JSON if json=True, Response object otherwise).
        """
        try:
            response = method(url, **kwargs)
        except requests.exceptions.ConnectionError:
            response = method(url, **kwargs)
        self.logger.info(
            f"[{self.__class__.__name__}] {method.__name__.upper()} {urlparse(url).path} > HTTP {response.status_code}"
        )
        if trigger_exception:
            response.raise_for_status()
        return response.json() if json else response

    def is_finding_processable(self, finding: Finding) -> bool:
        """Check if a finding can be processed by this integration.

        Args:
            finding: The finding to check.

        Returns:
            True if the finding can be processed, False otherwise.
        """
        return finding.__class__ in self.finding_types or len(self.finding_types) == 0

    def _process_finding(self, execution: Execution, finding: Finding) -> None:
        """Process a single finding (to be implemented by subclasses).

        Args:
            execution: The execution context.
            finding: The finding to process.
        """
        pass

    def process_finding(self, execution: Execution, finding: Finding) -> None:
        """Process a finding if enabled and processable.

        Args:
            execution: The execution context.
            finding: The finding to process.
        """
        if not self.is_enabled() or not self.is_finding_processable(finding):
            return
        self._process_finding(execution, finding)

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Process multiple findings.

        Args:
            execution: The execution context.
            findings: List of findings to process.
        """
        if not self.is_enabled():
            return
        for finding in findings:
            self.process_finding(execution, finding)


class BaseNotification(BasePlatform):
    """Base class for notification systems.

    This abstract base class provides functionality for sending notifications
    to users about executions and alerts. It includes user filtering and
    notification scope management.

    Attributes:
        enable_field (str): User field name that controls notification enablement.
    """

    enable_field = ""

    def is_enabled(self, user: Any) -> bool:
        """Check if notifications are enabled for a user.

        Args:
            user: The user to check.

        Returns:
            True if notifications are enabled for the user.
        """
        return getattr(user, self.enable_field)

    def _notify(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        """Send notification to users (to be implemented by subclasses).

        Args:
            users: List of users to notify.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        pass

    def _notify_if_available(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        """Send notification if platform is available.

        Args:
            users: List of users to notify.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        if self.is_available():
            self._notify(users, *args, **kwargs)

    def _notify_if_enabled(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        """Send notification to enabled users if platform is available.

        Args:
            users: List of users to check and notify.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        if self.is_available():
            for user in users:
                if self.is_enabled(user):
                    self._notify([user], *args, **kwargs)

    def _get_users_to_notify_execution(self, execution: Execution) -> list[Any]:
        """Get users to notify about an execution.

        Args:
            execution: The execution to notify about.

        Returns:
            List of users who should be notified.
        """
        users = set()
        if execution.task.executor.notification_scope != Notification.DISABLED and getattr(
            execution.task.executor, self.enable_field
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

    def _notify_execution(self, users: list[Any], execution: Execution, findings: list[Finding]) -> None:
        """Send execution notification to users (to be implemented by subclasses).

        Args:
            users: List of users to notify.
            execution: The execution to notify about.
            findings: List of findings from the execution.
        """
        pass

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Process findings by sending execution notifications.

        Args:
            execution: The execution context.
            findings: List of findings to process.
        """
        if not self.is_available():
            return
        self._notify_execution(self._get_users_to_notify_execution(execution), execution, findings)

    def _get_users_to_notify_alert(self, alert: Alert) -> list[Any]:
        """Get users to notify about an alert.

        Args:
            alert: The alert to notify about.

        Returns:
            List of users who should be notified.
        """
        return alert.subscribers.filter(**{self.enable_field: True}).all()

    def _notify_alert(self, users: list[Any], alert: Alert, finding: Finding) -> None:
        """Send alert notification to users (to be implemented by subclasses).

        Args:
            users: List of users to notify.
            alert: The alert to notify about.
            finding: The finding that triggered the alert.
        """
        pass

    def process_alert(self, alert: Alert, finding: Finding) -> None:
        """Process alert by sending notifications to subscribers.

        Args:
            alert: The alert to process.
            finding: The finding that triggered the alert.
        """
        if not self.is_available():
            return
        self._notify_alert(alert.subscribers.filter(**{self.enable_field: True}).all(), alert, finding)

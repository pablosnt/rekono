"""Base classes of the integrations with external platforms.

Rekono integrates with three kinds of platforms: the ones that receive the findings
of the executions, the ones that provide extra information about the CVEs, and the
ones that notify the users. All of them process the findings of an execution, so
they share the entry points defined here.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdown import markdown
from requests.adapters import HTTPAdapter, Retry

from alerts.models import Alert
from executions.models import Execution
from findings.enums import Severity
from findings.framework.models import Finding
from findings.models import Vulnerability
from framework.logging import LoggingEntity
from integrations.models import Integration
from users.enums import Notification


class BasePlatform(LoggingEntity):
    """Base platform, which every external platform of Rekono extends."""

    def is_available(self) -> bool:
        """Check if the platform can be used.

        Returns:
            True, unless the platform overrides this check.
        """
        return True

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Process the findings of an execution, as implemented by each platform.

        Args:
            execution: Execution that reported the findings.
            findings: Findings to be processed.
        """
        pass


class BaseIntegration(BasePlatform):
    """Base platform of the ones whose API Rekono consumes.

    Attributes:
        url: Base URL of the external API.
        finding_types: Finding models that this integration processes, or empty to
          process all of them.
        timeout: Connection and read timeouts in seconds applied to every request.
    """

    url = ""
    finding_types = []
    # The read timeout is the more generous one because some platforms are slow to answer,
    # but none of them should take more than a few seconds to connect
    timeout = (5, 30)

    @cached_property
    def integration(self) -> Integration:
        """The integration entity of this platform, identified by its class name."""
        return Integration.objects.get(key=self.__class__.__name__.lower())

    @cached_property
    def session(self) -> requests.Session:
        """The HTTP session used for all the requests, which retries the failed ones."""
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
        """Check if this integration is enabled by the administrators.

        Returns:
            Whether the integration is enabled. False when its entity doesn't exist
            yet, so a missing integration is never used.
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
        """Perform an HTTP request to the external API and log its result.

        The timeout is applied to every request, unless the caller passes its own one,
        because the Retry policy only covers connection errors and HTTP status codes,
        not a response that never arrives.

        Args:
            method: Method of the session that performs the request, like session.get.
            url: URL to be requested.
            json: Whether to return the parsed JSON response instead of the response.
            trigger_exception: Whether to raise an exception for error status codes.
            **kwargs: Extra arguments for the request, like the body or the headers.

        Returns:
            The parsed JSON response, or the response itself if json is disabled.
        """
        kwargs.setdefault("timeout", self.timeout)
        try:
            response = method(url, **kwargs)
        except requests.exceptions.ConnectionError:
            # Connection errors aren't covered by the status-based Retry adapter, so retry once here
            response = method(url, **kwargs)
        self.logger.info(
            f"[{self.__class__.__name__}] {method.__name__.upper()} {urlparse(url).path} > HTTP {response.status_code}"
        )
        if trigger_exception:
            response.raise_for_status()
        return response.json() if json else response

    def is_finding_processable(self, finding: Finding) -> bool:
        """Check if a finding is one of the types that this integration processes.

        Args:
            finding: Finding whose type is checked.

        Returns:
            Whether the finding can be processed. True for every finding when the
            integration doesn't declare any type.
        """
        return finding.__class__ in self.finding_types or len(self.finding_types) == 0

    def _process_finding(self, execution: Execution, finding: Finding) -> None:
        """Process one finding, as implemented by each integration.

        Args:
            execution: Execution that reported the finding.
            finding: Finding to be processed.
        """
        pass

    def process_finding(self, execution: Execution, finding: Finding) -> None:
        """Process one finding if this integration is enabled and processes its type.

        Availability is deliberately not checked here, because this method is called once per
        finding and checking it would perform one live request to the external API for every
        finding, including the ones that this integration doesn't even process. Callers check
        it once before processing the findings of an execution, so an unavailable integration
        is discarded before reaching this point.

        Any failure is logged rather than propagated, so a caller processing a batch of
        findings doesn't lose the remaining ones because this integration failed for one.

        Args:
            execution: Execution that reported the finding.
            finding: Finding to be processed.
        """
        # The finding type is checked first because it's the only check that doesn't query anything
        if not self.is_finding_processable(finding) or not self.is_enabled():
            return
        try:
            self._process_finding(execution, finding)
        except Exception as ex:
            self.logger.error(
                f"[{self.__class__.__name__}] Error processing finding {finding.id} from execution {execution.id}: {str(ex)}"
            )

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Process all the findings of an execution, one by one.

        Skips processing entirely when the integration is disabled or unavailable. This is
        the only place where availability is checked, once per execution, so the findings are
        processed without performing one live request to the external API per finding.
        Failures affecting one finding are contained by process_finding, so they don't
        stop the remaining findings from being processed.

        Args:
            execution: Execution that reported the findings.
            findings: Findings to be processed.
        """
        if not self.is_enabled() or not self.is_available():
            return
        for finding in findings:
            self.process_finding(execution, finding)


class BaseCveProvider(BaseIntegration):
    """Base platform of the ones that know extra information about the CVEs.

    Subclasses implement _get_cve and _parse_cve for their own API, so all the
    providers return the same enrichment data and can be compared by its quality
    when several of them know the same CVE.

    Attributes:
        finding_types: Only vulnerabilities are enriched with CVE data.
        cvss_mapping: CVSS base score range of each Rekono severity.
    """

    finding_types = [Vulnerability]
    cvss_mapping = {
        Severity.CRITICAL: (9, 11),
        Severity.HIGH: (7, 9),
        Severity.MEDIUM: (4, 7),
        Severity.LOW: (2, 4),
        Severity.INFO: (0, 2),
    }

    @dataclass
    class CveEnrichment:
        """Information about a CVE, in the common format of all the providers.

        Attributes:
            name: Vulnerability name or advisory title.
            description: Full technical vulnerability description.
            cwes: CWE identifiers in CWE-NNN format.
            cvss_base_score: Numeric CVSS base score.
            cvss_vector: Full CVSS vector string.
            cvss_version: CVSS version prefix (e.g. "3.1", "4.0").
            epss_score: EPSS probability of exploitation (0.0-1.0).
            epss_percentile: EPSS percentile rank among all CVEs (0.0-1.0).
            technologies: Affected product or package identifiers.
            reference: Canonical vulnerability detail page URL.
            status: Provider-specific advisory status string.
            euvd_id: ENISA EUVD identifier.
            ghsa_id: GitHub Security Advisory identifier.
            osv_generic_id: OSV-native ID for non-CVE/GHSA/EUVD ecosystems.
        """

        name: str | None = None
        description: str | None = None
        cwes: list[str] | None = None
        cvss_base_score: float | None = None
        cvss_vector: str | None = None
        cvss_version: str | None = None
        epss_score: float | None = None
        epss_percentile: float | None = None
        technologies: list[str] | None = None
        reference: str | None = None
        status: str | None = None
        euvd_id: str | None = None
        ghsa_id: str | None = None
        osv_generic_id: str | None = None

    def is_available(self) -> bool:
        """Check if the provider answers with data, which also validates the API token.

        Returns:
            Whether the provider answered with data about a well-known CVE. False
            for any failure, including an invalid or missing API token.
        """
        try:
            # Test connectivity using Log4Shell as a well-known, reliably indexed CVE
            return bool(self._get_cve("CVE-2021-44228"))
        except Exception:
            return False

    def _get_cve(self, cve: str) -> dict[str, Any]:
        """Get the raw data of a CVE from the provider API, as each provider does.

        Args:
            cve: CVE identifier in CVE-YYYY-NNNN form.

        Returns:
            No data, unless the provider overrides this method.
        """
        return {}  # pragma: no cover

    def _parse_cve(self, cve: str, data: list[dict[str, Any]] | dict[str, Any]) -> CveEnrichment | None:
        """Parse the raw data of a CVE into the common format, as each provider does.

        Args:
            cve: CVE identifier in CVE-YYYY-NNNN form.
            data: Raw response of the provider API, as returned by _get_cve.

        Returns:
            The enrichment data, or None if the response doesn't include any useful
            information about the CVE.
        """
        return None

    def get_cve(self, cve: str) -> CveEnrichment | None:
        """Get the information that this provider has about a CVE.

        A provider that fails for this CVE is logged and treated as having no data, so
        the callers querying several providers still apply the data returned by the
        others, and a provider outage never interrupts the findings processing.

        Args:
            cve: CVE identifier in CVE-YYYY-NNNN form.

        Returns:
            The enrichment data, or None if the provider doesn't know the CVE or
            fails to answer.
        """
        try:
            data = self._get_cve(cve)
            return self._parse_cve(cve, data) if data else None
        except Exception as ex:
            self.logger.error(f"[{self.__class__.__name__}] Error getting {cve} data: {str(ex)}")
            return None

    def cve_quality_score(self, data: CveEnrichment) -> int:
        """Calculate how complete the information provided about a CVE is.

        Scores start at 10 and are reduced most heavily for a missing description,
        then for missing CWE or affected technology data, and for missing or
        outdated CVSS data. A small bonus applies when EPSS scores or an alternate
        identifier (EUVD, GHSA, or OSV) is present. Subclasses may override to
        apply provider-specific adjustments.

        Args:
            data: Enrichment data whose completeness is measured.

        Returns:
            The quality score, used to select the best provider when several of them
            know the same CVE.
        """
        score = 10
        if not data.description:
            score -= 8
        if len(data.cwes or []) == 0 or len(list(data.technologies or [])) == 0:
            score -= 3
        if not data.cvss_base_score or not data.cvss_version or not data.cvss_vector:
            score -= 5
        elif data.cvss_version.startswith("2"):
            score -= 2
        if (data.epss_score and data.epss_percentile) or data.euvd_id or data.ghsa_id or data.osv_generic_id:
            score += 1
        return score

    def save(self, finding: Vulnerability, data: CveEnrichment) -> None:
        """Apply the information about a CVE to the vulnerability that reports it.

        The severity is not taken from the provider, but derived from the CVSS base
        score using the cvss_mapping ranges, so all the vulnerabilities are rated
        the same way regardless of the provider that enriched them.

        Args:
            finding: Vulnerability to be enriched, which is updated and saved.
            data: Enrichment data to apply to it.
        """
        finding.name = data.name
        # Some providers return the description as Markdown starting with a heading; render it to
        # HTML and strip the tags to plain text, doubling newlines to keep paragraph breaks
        finding.description = (
            BeautifulSoup(markdown(data.description), features="html.parser").get_text().replace("\n", "\n\n")
            if data.description and data.description.startswith("#")
            else data.description
        )
        cwes = []
        for _cwe in set(data.cwes or []):
            cwe = _cwe.upper()
            if cwe.startswith("CWE-") and cwe.replace("CWE-", "").isdigit():
                cwes.append(cwe)
        finding.cwes = sorted(cwes, key=lambda c: int(c.split("-", 1)[1]))
        if data.cvss_base_score:
            finding.severity = next(
                (
                    k
                    for k, v in self.cvss_mapping.items()
                    if data.cvss_base_score >= v[0] and data.cvss_base_score < v[1]
                ),
                Severity.MEDIUM,
            )
            finding.cvss_base_score = data.cvss_base_score
        finding.cvss_vector = data.cvss_vector
        finding.cvss_version = data.cvss_version
        finding.epss_score = data.epss_score
        finding.epss_percentile = data.epss_percentile
        finding.reference = data.reference
        finding.euvd_id = data.euvd_id
        finding.ghsa_id = data.ghsa_id
        finding.osv_generic_id = data.osv_generic_id
        finding.save(
            update_fields=[
                "name",
                "description",
                "cwes",
                "severity",
                "cvss_base_score",
                "cvss_vector",
                "cvss_version",
                "epss_score",
                "epss_percentile",
                "reference",
                "euvd_id",
                "ghsa_id",
                "osv_generic_id",
            ]
        )

    def is_finding_processable(self, finding: Finding) -> bool:
        """Check if a finding is a vulnerability with a CVE that can be enriched.

        Args:
            finding: Finding whose type and CVE are checked.

        Returns:
            Whether the finding can be enriched. False for the vulnerabilities
            without a CVE, since the providers are queried by CVE identifier.
        """
        return self.is_enabled() and super().is_finding_processable(finding) and finding.cve is not None


class BaseNotification(BasePlatform):
    """Base platform of the ones that notify the users.

    Attributes:
        enable_field: User field that tells if this notification channel is enabled
          for that user.
    """

    enable_field = ""

    def is_enabled(self, user: Any) -> bool:
        """Check if a user enabled this notification channel.

        Args:
            user: User whose notification preferences are checked.

        Returns:
            Whether that user wants to be notified through this channel.
        """
        return getattr(user, self.enable_field)

    def _notify(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        """Send a notification to some users, as implemented by each platform.

        Args:
            users: Users to be notified.
            *args: Content of the notification, defined by each platform.
            **kwargs: Content of the notification, defined by each platform.
        """
        pass

    def _notify_if_available(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        """Send a notification to some users only if the platform can be used.

        Args:
            users: Users to be notified, without checking their preferences.
            *args: Content of the notification, forwarded to _notify.
            **kwargs: Content of the notification, forwarded to _notify.
        """
        if self.is_available():
            self._notify(users, *args, **kwargs)

    def _notify_if_enabled(self, users: list[Any], *args: Any, **kwargs: Any) -> None:
        """Send a notification to each user that enabled this channel.

        Args:
            users: Candidate users, filtered by their notification preferences.
            *args: Content of the notification, forwarded to _notify.
            **kwargs: Content of the notification, forwarded to _notify.
        """
        if self.is_available():
            for user in users:
                if self.is_enabled(user):
                    self._notify([user], *args, **kwargs)

    def _get_users_to_notify_execution(self, execution: Execution) -> list[Any]:
        """Get the users to be notified about the result of an execution.

        Besides the project members that ask for all the executions, the user that
        executed the task is notified about their own executions, unless they only
        want to be notified about alerts. Everybody has to have this notification
        channel enabled, the executor included.

        Args:
            execution: Execution whose project members and executor are checked.

        Returns:
            The users to notify, without duplicates.
        """
        users = set()
        interested_users = execution.task.target.project.members.filter(
            **{
                self.enable_field: True,
                "notification_scope": Notification.ALL_EXECUTIONS,
            }
        )
        if execution.task.executor:
            if execution.task.executor.notification_scope != Notification.ONLY_ALERTS and getattr(
                execution.task.executor, self.enable_field
            ):
                users.add(execution.task.executor)
            users.update(interested_users.exclude(id=execution.task.executor.id))
        else:
            users.update(interested_users)
        return list(users)

    def _notify_execution(self, users: list[Any], execution: Execution, findings: list[Finding]) -> None:
        """Notify the result of an execution, as implemented by each platform.

        Args:
            users: Users to be notified.
            execution: Execution whose result is reported.
            findings: Findings reported by that execution.
        """
        pass

    def process_findings(self, execution: Execution, findings: list[Finding]) -> None:
        """Notify the interested users about the findings of an execution.

        Skips notifying when the integration is unavailable. Any failure while
        building or sending the notification is logged rather than propagated, so
        a broken notification channel never interrupts execution processing.

        Args:
            execution: Execution whose result is reported.
            findings: Findings reported by that execution.
        """
        if not self.is_available():
            return
        try:
            self._notify_execution(self._get_users_to_notify_execution(execution), execution, findings)
        except Exception as ex:
            self.logger.error(
                f"[{self.__class__.__name__}] Error processing {len(findings)} findings from execution {execution.id}: {str(ex)}"
            )

    def _get_users_to_notify_alert(self, alert: Alert) -> list[Any]:
        """Get the alert subscribers that enabled this notification channel.

        Args:
            alert: Alert whose subscribers are filtered.

        Returns:
            The subscribers that want to be notified through this channel.
        """
        return alert.subscribers.filter(**{self.enable_field: True}).all()

    def _notify_alert(self, users: list[Any], alert: Alert, finding: Finding) -> None:
        """Notify a triggered alert, as implemented by each platform.

        Args:
            users: Users to be notified.
            alert: Alert that was triggered.
            finding: Finding that triggered it.
        """
        pass

    def process_alert(self, alert: Alert, finding: Finding) -> None:
        """Notify the subscribers of an alert triggered by a finding.

        Args:
            alert: Alert that was triggered.
            finding: Finding that triggered it.
        """
        if not self.is_available():
            return
        self._notify_alert(alert.subscribers.filter(**{self.enable_field: True}).all(), alert, finding)

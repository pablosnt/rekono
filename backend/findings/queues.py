"""Queue that processes the findings reported by an execution.

The findings are enriched with the information of the CVE providers, sent to the
integrations, and notified to the users that are interested in them. The findings
that stop being detected are also fixed here.
"""

from django_rq import job
from rq.job import Job

from executions.enums import Status
from executions.models import Execution
from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Finding,
    Host,
    Path,
    Port,
    Technology,
    Vulnerability,
)
from framework.platforms import BaseCveProvider, BaseIntegration, BaseNotification
from framework.queues import BaseQueue
from platforms.cvecrowd.integrations import CveCrowd
from platforms.defectdojo.integrations import DefectDojo
from platforms.email.notifications import SMTP
from platforms.euvd import EUVD
from platforms.first import First
from platforms.ghsa import GHSA
from platforms.hacktricks import HackTricks
from platforms.hosts_metadata import HostsMetadata
from platforms.nvdnist.integrations import NvdNist
from platforms.osv import OSV
from platforms.telegram_app.notifications import Telegram
from platforms.virustotal.integrations import VirusTotal
from platforms.vulncheck.integrations import VulnCheck
from settings.models import Settings


class FindingsQueue(BaseQueue):
    """Queue that enriches, integrates, and notifies the findings.

    Attributes:
        name: Name of the RQ queue.
    """

    name = "findings"

    def enqueue(self, execution: Execution, findings: list[Finding]) -> Job:
        """Enqueue the findings reported by an execution.

        Args:
            execution: Execution that reported the findings. It is serialized as it
              is at this moment, so it must already be completed for its status and
              hash to reach the job.
            findings: Findings that the parser reported for that execution.

        Returns:
            The enqueued job, which processes the findings once a worker takes it.
        """
        job = super().enqueue(execution=execution, findings=findings)
        self.logger.info(f"[Findings] {len(findings)} findings from execution {execution.id} have been enqueued")
        return job

    @staticmethod
    def _consume(execution: Execution, findings: list[Finding]) -> None:
        """Run the findings processing pipeline for an execution.

        Args:
            execution: Execution that reported the findings. Its hash selects the
              previous executions that scanned the same thing, so a stale one would
              fix the findings of the wrong executions.
            findings: Findings that the parser reported for that execution.
        """
        BaseQueue.logger.info(
            f"[Findings] Processing of {len(findings)} findings from execution {execution.id} has started"
        )
        settings = Settings.objects.first()
        # Finding types with the field used to sort them and whether that sorting must be reversed
        finding_types = [
            (OSINT, "data", False),
            (Host, "ip", False),
            (Port, "port", False),
            (Path, "path", False),
            (Technology, "name", False),
            (Credential, "id", False),
            (Vulnerability, "severity", True),
            (Exploit, "id", False),
        ]
        if findings:
            cve_providers: list[BaseCveProvider] = [
                provider
                for provider in [VulnCheck(), NvdNist(), GHSA(), EUVD(), OSV()]
                if provider.is_enabled() and provider.is_available()
            ]
            integrations_per_finding: list[BaseIntegration] = [
                integration
                for integration in [HackTricks(), CveCrowd(), HostsMetadata(), VirusTotal(), First()]
                if integration.is_enabled() and integration.is_available()
            ]
            integrations_per_execution: list[BaseIntegration] = [DefectDojo()]
            notifications: list[BaseNotification] = [SMTP(), Telegram()]
            for finding in findings:
                # Auto-fix reactivates a finding that was previously marked as fixed
                # but has reappeared in this execution
                if settings.auto_fix_findings and finding.is_fixed:
                    finding.__class__.objects.remove_fix(finding)
                # CVE enrichment runs first so the other integrations see the enriched finding
                cve_enrichments: list[tuple[BaseCveProvider, int, BaseCveProvider.CveEnrichment]] = []
                for cve_provider in cve_providers:
                    if cve_provider.is_finding_processable(finding):
                        enrichment = cve_provider.get_cve(finding.cve)
                        if enrichment:
                            # Track each candidate provider alongside its quality score and data
                            # so the best one can be picked once every provider has been queried
                            cve_enrichments.append(
                                (cve_provider, cve_provider.cve_quality_score(enrichment), enrichment)
                            )
                if len(cve_enrichments) > 0:
                    # Highest quality score wins when multiple providers return data for the same CVE
                    cve_enrichments.sort(key=lambda x: x[1], reverse=True)
                    cve_provider, _, enrichment = cve_enrichments[0]
                    if cve_provider and enrichment:
                        cve_provider.save(finding, enrichment)
                for integration in integrations_per_finding:
                    integration.process_finding(execution, finding)
                # The alerts are ordered by item so the most specific ones are checked first
                for alert in execution.task.target.project.alerts.filter(enabled=True).order_by("-item").all():
                    if alert.must_be_triggered(execution, finding):
                        for platform in notifications:
                            platform.process_alert(alert, finding)
            # Sort findings by relevant field, so the integrations and notifications report them in a meaningful order
            findings_per_type = {
                finding_type: sorted(
                    [finding for finding in findings if isinstance(finding, finding_type)],
                    key=lambda finding: getattr(finding, ordering),
                    reverse=reverse,
                )
                for finding_type, ordering, reverse in finding_types
            }
            sorted_findings = sum(findings_per_type.values(), [])
            for platform in integrations_per_execution + notifications:
                platform.process_findings(execution, sorted_findings)
        if settings.auto_fix_findings:
            # The execution hash identifies the executions that scanned the same thing in the same
            # way, so a finding that they discovered before and this one didn't is gone
            for finding_type, _, _ in finding_types:
                finding_type.objects.fix(
                    finding_type.objects.filter(
                        executions__task__target=execution.task.target,
                        executions__hash=execution.hash,
                        executions__status__in=Status.finished(),
                    )
                    .exclude(executions__id=execution.id)
                    .distinct()
                )

    @staticmethod
    @job("findings")
    def consume(execution: Execution, findings: list[Finding]) -> None:
        """Process the findings of one execution.

        Any failure raised by the pipeline is logged rather than propagated, so the
        RQ job always completes successfully.

        Args:
            execution: Execution that reported the findings, as it was when the job
              was enqueued. It must already be completed by then, since its status
              and hash are read here from the pickled copy.
            findings: Findings that the parser reported for that execution.
        """
        self = FindingsQueue()
        # Lock RQ per target to avoid getting multiple workers processing the same findings at the same time
        with self.queue.connection.lock(f"findings:{execution.task.target.id}"):
            try:
                FindingsQueue._consume(execution, findings)
            except Exception as ex:
                self.logger.error(
                    f"[{self.__class__.__name__}] Error processing {len(findings)} findings from execution {execution.id}: {str(ex)}"
                )

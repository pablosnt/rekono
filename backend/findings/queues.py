"""Background job queue processing for security findings.

Handles asynchronous processing of security findings through background job
queues including external platform integration, notifications, and automatic
finding lifecycle management.
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
    """Background job queue for asynchronous findings processing.

    Manages background processing of security findings including external
    platform integrations, alert notifications, and automatic finding
    lifecycle management with Redis Queue (RQ) backend.
    """

    name = "findings"

    def enqueue(self, execution: Execution, findings: list[Finding]) -> Job:
        """Enqueue findings for background processing.

        Adds findings to the background job queue for asynchronous
        processing and logs the enqueue operation.

        Args:
            execution (Execution): Execution that produced the findings.
            findings (list[Finding]): List of findings to process.

        Returns:
            Job: Queued job object for tracking.
        """
        job = super().enqueue(execution=execution, findings=findings)
        self.logger.info(f"[Findings] {len(findings)} findings from execution {execution.id} have been enqueued")
        return job

    @staticmethod
    @job("findings")
    def consume(execution: Execution, findings: list[Finding]) -> None:
        """Process findings through background job workflow.

        Executes complete findings processing pipeline including external
        platform integrations, alert notifications, and automatic fixing
        based on system settings and project configuration.

        Processing Steps:
            - CVE enrichment via multiple providers with quality-score selection
            - Per-finding integrations
            - Per-execution integrations
            - Alert notification dispatch
            - Automatic finding lifecycle management and cross-execution fix correlation

        Args:
            execution (Execution): Source execution for the findings.
            findings (list[Finding]): List of findings to process.
        """
        settings = Settings.objects.first()
        if findings:
            # Initialize integration and notification platforms
            cve_providers: list[BaseCveProvider] = [VulnCheck(), NvdNist(), GHSA(), EUVD(), OSV()]
            integrations_per_finding: list[BaseIntegration] = [
                HackTricks(),
                CveCrowd(),
                HostsMetadata(),
                VirusTotal(),
                First(),
            ]
            integrations_per_execution: list[BaseIntegration] = [DefectDojo()]
            notifications: list[BaseNotification] = [SMTP(), Telegram()]
            # Process each finding individually
            for finding in findings:
                # Reactivate previously fixed findings if auto-fix is enabled
                # This ensures findings that reappear are marked as active again
                if settings.auto_fix_findings and finding.is_fixed:
                    finding.__class__.objects.remove_fix(finding)
                # Enrich CVEs information before processing the other integrations
                cve_enrichments: list[tuple[BaseCveProvider, int, BaseCveProvider.CveEnrichment]] = []
                for cve_provider in cve_providers:
                    if cve_provider.is_finding_processable(finding):
                        # Get CVE information from the provider
                        enrichment = cve_provider.get_cve(finding.cve)
                        if enrichment:
                            # Save the provider, its data quality score, and its data
                            cve_enrichments.append(
                                (cve_provider, cve_provider.cve_quality_score(enrichment), enrichment)
                            )
                if len(cve_enrichments) > 0:
                    # Get the CVE data with the highest data quality score
                    cve_enrichments.sort(key=lambda x: x[1], reverse=True)
                    cve_provider, _, enrichment = cve_enrichments[0]
                    if cve_provider and enrichment:
                        # Save the CVE enriched information in the finding
                        cve_provider.save(finding, enrichment)
                # Process findings through integrations that work on individual findings
                for integration in integrations_per_finding:
                    integration.process_finding(execution, finding)
                # Check and trigger project alerts for this specific finding
                for alert in execution.task.target.project.alerts.filter(enabled=True).order_by("-item").all():
                    if alert.must_be_triggered(execution, finding):
                        # Send notifications through all configured notification platforms
                        for platform in notifications:
                            platform.process_alert(alert, finding)
            # Process findings through platforms that run per execution
            for platform in integrations_per_execution + notifications:
                platform.process_findings(execution, findings)
        # Automatic fixing: mark findings as fixed if they're no longer detected in identical execution contexts
        if settings.auto_fix_findings:
            # For each finding type, mark findings as fixed if they don't appear in the current execution
            # but were found in previous executions with the same parameters
            for finding_type in [
                OSINT,
                Host,
                Port,
                Path,
                Technology,
                Credential,
                Vulnerability,
                Exploit,
            ]:
                finding_type.objects.fix(
                    finding_type.objects.filter(
                        executions__hash=execution.hash,
                        executions__status=Status.COMPLETED,
                    )
                    .exclude(executions__id=execution.id)
                    .distinct()
                )

"""Background job queue processing for findings.

This module handles the asynchronous processing of security findings
through background job queues. It manages the integration with external
platforms, notifications, and automatic fixing of findings based on
execution results.
"""

from backend.framework.platforms import BaseIntegration
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
from framework.queues import BaseQueue
from platforms.cvecrowd.integrations import CveCrowd
from platforms.defectdojo.integrations import DefectDojo
from platforms.hacktricks import HackTricks
from platforms.hosts_metadata import HostsMetadata
from platforms.mail.notifications import SMTP
from platforms.nvdnist.integrations import NvdNist
from platforms.telegram_app.notifications.notifications import Telegram
from settings.models import Settings


class FindingsQueue(BaseQueue):
    """Background job queue for processing security findings.

    Handles the asynchronous processing of findings discovered during
    security assessments, including integration with external platforms,
    notifications, and automatic fixing of findings.
    """

    name = "findings"

    def enqueue(self, execution: Execution, findings: list[Finding]) -> Job:
        """Enqueue findings for background processing.

        Adds findings to the background job queue for asynchronous
        processing and logs the enqueue operation.

        Args:
            execution: The execution that produced the findings.
            findings: List of findings to process.

        Returns:
            The queued job object.
        """
        job = super().enqueue(execution=execution, findings=findings)
        self.logger.info(f"[Findings] {len(findings)} findings from execution {execution.id} have been enqueued")
        return job

    @staticmethod
    @job("findings")
    def consume(execution: Execution, findings: list[Finding]) -> None:
        """Process findings in the background.

        Handles the main processing logic for findings, including:
        - Integration with external platforms (DefectDojo, NVD, etc.)
        - Sending notifications via email and Telegram
        - Automatic fixing of findings based on settings
        - Processing alerts for enabled project alerts

        Args:
            execution: The execution that produced the findings.
            findings: List of findings to process.
        """
        settings = Settings.objects.first()
        if findings:
            # Initialize integration and notification platforms
            integrations = [DefectDojo(), NvdNist(), HackTricks(), CveCrowd(), HostsMetadata()]
            notifications = [SMTP(), Telegram()]
            # Process each finding individually
            for finding in findings:
                # Keep finding active if auto_fix is enabled
                if settings.auto_fix_findings and finding.is_fixed:
                    finding.__class__.objects.remove_fix(finding)
                # Process through integrations
                for integration in integrations:
                    if integration.run_per_execution:
                        continue
                    integration.process_finding(execution, finding)
                # Process alerts for the finding
                for alert in execution.task.target.project.alerts.filter(enabled=True).order_by("-item").all():
                    if alert.must_be_triggered(execution, finding):
                        for platform in notifications:
                            platform.process_alert(alert, finding)
            # Process findings through platforms that run per execution
            for platform in integrations + notifications:
                if isinstance(platform, BaseIntegration) and not platform.run_per_execution:
                    continue
                platform.process_findings(execution, findings)
        # Handle automatic fixing of findings from same execution hash that are not longer detected
        if settings.auto_fix_findings:
            same_executions = Execution.objects.filter(hash=execution.hash, status=Status.COMPLETED)
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
                    finding_type.objects.exclude(executions__id=execution.id)
                    .filter(executions__in=same_executions)
                    .all()
                )

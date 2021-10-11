from django_rq import job
from executions.models import Execution
from findings.models import Vulnerability
from findings.enums import Severity
from integrations.nist import cve


@job('findings-queue')
def process_findings(execution: Execution = None, findings: list = []) -> None:
    if execution:
        for finding in findings:
            setattr(finding, 'execution', execution)
            if isinstance(finding, Vulnerability) and finding.cve:
                cve_info = cve.get_information(finding.cve)
                finding.description = cve_info.get('description', '')
                finding.severity = cve_info.get('severity', Severity.MEDIUM)
                finding.reference = cve_info.get('reference', '')
            finding.save()

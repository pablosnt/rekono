from django_rq import job
from executions.models import Execution
from findings.models import Vulnerability
from findings import cve_nist


@job('findings-queue')
def process_findings(execution: Execution = None, findings: list = []) -> None:
    if execution:
        for finding in findings:
            setattr(finding, 'execution', execution)
            if isinstance(finding, Vulnerability) and finding.cve:
                cve_info = cve_nist.get_information(finding.cve)
                finding.description = cve_info.get('description', '')
                finding.severity = cve_info.get('severity', Vulnerability.Severity.MEDIUM)
                finding.reference = cve_info.get('reference', '')
            finding.save()

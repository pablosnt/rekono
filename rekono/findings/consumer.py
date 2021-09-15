from executions.models import Execution
from django_rq import job


@job('finding-queue')
def get_findings(execution: Execution = None, findings: list = []) -> None:
    if execution:
        for finding in findings:
            setattr(finding, 'execution', execution)
            finding.save()


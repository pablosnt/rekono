from tools.enums import FindingType
from tools import utils
from tools.models import Input
import django_rq


finding_relations = {
    FindingType.OSINT: [],
    FindingType.HOST: [],
    FindingType.ENUMERATION: [FindingType.HOST],
    FindingType.HTTP_ENDPOINT: [FindingType.ENUMERATION],
    FindingType.TECHNOLOGY: [FindingType.ENUMERATION],
    FindingType.VULNERABILITY: [FindingType.TECHNOLOGY],
    FindingType.EXPLOIT: [FindingType.TECHNOLOGY, FindingType.VULNERABILITY]
}


def cancel_execution(job_id) -> None:
    executions_queue = django_rq.get_queue('executions-queue')
    execution = executions_queue.fetch_job(job_id)
    execution.cancel()


def get_findings_from_dependencies(dependencies: list) -> dict:
    findings = {}
    executions_queue = django_rq.get_queue('executions-queue')
    for dep_id in dependencies:
        dependency = executions_queue.fetch_job(dep_id)
        if not dependency or not dependency.result:
            continue
        for input_type in finding_relations.keys():
            input_class = utils.get_finding_class_by_type(input_type)
            filter = [f for f in dependency.result.findings if isinstance(f, input_class)]
            for finding in filter:
                if input_type in findings:
                    findings[input_type].append(finding)
                else:
                    findings[input_type] = [finding]
    return findings


def get_jobs_from_findings(findings: dict, inputs: list) -> dict:
    job_counter = 0
    jobs = {
        job_counter: []
    }
    for input_type in finding_relations.keys():
        input_class = utils.get_finding_class_by_type(input_type)
        filter = [i for i in inputs if (
            i.type == input_type or
            (
                i.type == FindingType.URL and
                input_type in [FindingType.HOST, FindingType.ENUMERATION]
            ))]
        if not filter or input_type not in findings:
            continue
        for i in filter:
            if finding_relations[input_type]:
                relations_found = False
                for finding in findings[input_type]:
                    for relation in finding_relations[input_type]:
                        if hasattr(finding, relation.name.lower()):
                            attribute = getattr(finding, relation.name.lower(), None)
                            if attribute:
                                relations_found = True
                                for jc in jobs.copy():
                                    if attribute in jobs[jc]:
                                        if i.selection == Input.InputSelection.ALL:
                                            jobs[jc].append(finding)
                                        else:
                                            related_items = [
                                                f for f in jobs[jc]
                                                if not isinstance(f, input_class)
                                            ]
                                            if len(related_items) < len(jobs[jc]):
                                                jobs[job_counter] = related_items.copy()
                                                jobs[job_counter].append(finding)
                                                job_counter += 1
                                            else:
                                                jobs[jc].append(finding)
                                break
                    if not relations_found:
                        for jc in jobs.copy():
                            jobs[jc].append(finding)
            else:
                if i.selection == Input.InputSelection.ALL:
                    for jc in jobs.copy():
                        jobs[jc].extend(findings[input_type])
                else:
                    aux = jobs[job_counter].copy()
                    for finding in findings[input_type]:
                        jobs[job_counter] = aux.copy()
                        jobs[job_counter].append(finding)
                        job_counter += 1
    return jobs

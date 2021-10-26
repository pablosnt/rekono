import rq
from django_rq import job
from executions.models import Execution
from executions.queue import producer
from executions.queue import utils as queue_utils
from executions.queue.constants import finding_relations
from processes.executor import success_callback
from rq.job import Job
from tools import utils as tool_utils
from tools.enums import InputSelection
from tools.exceptions import InvalidToolParametersException
from tools.models import Configuration, Intensity, Tool
from tools.tools.base_tool import BaseTool


@job('executions-queue')
def consumer(
    execution: Execution,
    tool: Tool,
    configuration: Configuration,
    intensity: Intensity,
    inputs: list,
    target_ports: list,
    parameters: list,
    previous_findings: list,
    domain: str,
) -> None:
    current_job = rq.get_current_job()
    tool_class = tool_utils.get_tool_class_by_name(tool.name)
    tool = tool_class(
        execution=execution,
        tool=tool,
        configuration=configuration,
        inputs=inputs,
        intensity=intensity,
        target_ports=target_ports,
    )
    if not previous_findings and current_job._dependency_ids:
        previous_findings = process_dependencies(
            execution,
            intensity,
            inputs,
            parameters,
            domain,
            current_job,
            tool
        )
    tool.run(parameters=parameters, previous_findings=previous_findings, domain=domain)
    return tool


def process_dependencies(
    execution: Execution,
    intensity: Intensity,
    inputs: list,
    parameters: list,
    domain: str,
    current_job: Job,
    tool: BaseTool
) -> list:
    findings = queue_utils.get_findings_from_dependencies(current_job._dependency_ids)
    if not findings:
        return []
    new_jobs_ids = []
    all_params = get_new_jobs_from_findings(findings, inputs)
    all_params = [
        list(param_set) for param_set in list(all_params)
        if check_params_for_tool(tool, parameters, list(param_set))
    ]
    for param_set in all_params[1:]:
        new_execution = Execution.objects.create(task=execution.task, step=execution.step)
        new_execution.save()
        job = producer.producer(
            new_execution,
            intensity,
            inputs,
            parameters=parameters,
            previous_findings=param_set,
            target_ports=tool.target_ports,
            domain=domain,
            callback=success_callback,
            at_front=True
        )
        new_jobs_ids.append(job.id)
    queue_utils.update_new_dependencies(current_job.id, new_jobs_ids, parameters)
    return next(iter(all_params), [])


def check_params_for_tool(tool: BaseTool, parameters: list, findings: list) -> bool:
    try:
        parameters, findings = tool.prepare_parameters(parameters, findings)
        tool.get_arguments(parameters, findings)
        return True
    except InvalidToolParametersException:
        return False


def get_new_jobs_from_findings(findings: dict, inputs: list) -> set:
    job_counter = 0
    jobs = {
        job_counter: []
    }
    for input_type in finding_relations.keys():
        input_class = tool_utils.get_finding_class_by_type(input_type)
        inputs = [i for i in inputs if i.type == input_type]
        if not inputs or input_type not in findings:
            continue
        for i in inputs:
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
                                        if i.selection == InputSelection.ALL:
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
                if i.selection == InputSelection.ALL:
                    for jc in jobs.copy():
                        jobs[jc].extend(findings[input_type])
                else:
                    aux = jobs[job_counter].copy()
                    for finding in findings[input_type]:
                        jobs[job_counter] = aux.copy()
                        jobs[job_counter].append(finding)
                        job_counter += 1
    return set(tuple(params) for params in jobs.values())

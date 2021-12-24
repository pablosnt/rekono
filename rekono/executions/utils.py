from tools import utils as tool_utils
from tools.enums import InputSelection


def get_executions_from_findings(findings: dict, inputs: list) -> set:
    job_counter = 0
    jobs = {
        job_counter: []
    }
    finding_relations = tool_utils.get_relations_between_input_types()
    for input_type in finding_relations.keys():
        if input_type not in findings:
            continue
        input_classes = tool_utils.get_finding_class_by_input_type(input_type)
        for i in [i for i in inputs if i.type == input_type]:
            if finding_relations[input_type]:
                relations_found = False
                for finding in findings[input_type]:
                    for relation in finding_relations[input_type]:
                        attribute = getattr(finding, relation.name.lower(), None)
                        if attribute:
                            for jc in jobs.copy():
                                if attribute in jobs[jc]:
                                    relations_found = True
                                    if i.selection == InputSelection.ALL:
                                        jobs[jc].append(finding)
                                    else:
                                        for input_class in input_classes:
                                            related_items = [
                                                f for f in jobs[jc] if not isinstance(
                                                    f,
                                                    input_class
                                                )
                                            ]
                                            if related_items:
                                                break
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
    executions = set(tuple(params) for params in jobs.values())
    return [list(param_set) for param_set in list(executions)]

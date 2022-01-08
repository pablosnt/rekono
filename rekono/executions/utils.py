from django.apps import apps
from inputs import utils
from tools.models import Argument, Tool


# TODO
def get_executions_from_findings(findings: dict, tool: Tool) -> set:
    executions = []
    finding_relations = utils.get_relations_between_input_types()
    for input_type, related_input_types in [(k, v) for k, v in finding_relations.items() if k.name in findings]:
        for related in related_input_types:
            for execution in executions:
                for finding in execution:
                    if 



































def get_executions_from_findings(findings: dict, arguments: list) -> set:
    job_counter = 0
    jobs = {
        job_counter: []
    }
    finding_relations = utils.get_relations_between_input_types()
    for input_type in finding_relations.keys():
        if input_type.name not in findings:
            continue
        app_label, model_name = input_type.related_model.split('.', 1)
        model = apps.get_model(app_label=app_label, model_name=model_name)
        arguments = Argument.objects.filter(inputs__type=input_type, order=1).all()
        if len(arguments) == 0:
            arguments = Argument.objects.filter(inputs__type=input_type, order__gt=1).all()
        for argument in arguments:
            if finding_relations[input_type.name]:
                relation_found = False
                for finding in findings[input_type.name]:
                    for relation in finding_relations[input_type.name]:
                        attribute = getattr(finding, relation.name.lower(), None)
                        if attribute:
                            for jc in jobs.copy():
                                if attribute in jobs[jc]:
                                    relation_found = True
                                    if argument.multiple:
                                        jobs[jc].append(finding)
                                    else:
                                        pass
                    if not relation_found:
                        for jc in jobs.copy():
                            jobs[jc].append(finding)
            else:
                if argument.multiple:
                    for jc in jobs.copy():
                        jobs[jc].extend(findings[input_type.name])
                else:
                    aux = jobs[job_counter].copy()
                    for finding in findings[input_type.name]:
                        jobs[job_counter] = aux.copy()
                        jobs[job_counter].append(finding)
                        job_counter += 1


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


        for i in [i for i in inputs if i.type == input_type]:
            if finding_relations[input_type.name]:
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

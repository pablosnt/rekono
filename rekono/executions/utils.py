from django.apps import apps
from input_types import utils
from input_types.base import BaseInput
from input_types.models import InputType
from tools.models import Argument, Tool


def select_argument(tool: Tool, input_type: InputType) -> Argument:
    argument = Argument.objects.filter(
        tool=tool,
        inputs__type=input_type,
        inputs__order=1
    ).first()
    if not argument:
        argument = Argument.objects.filter(
            tool=tool,
            inputs__type=input_type,
            inputs__order__gt=1
        ).first()
    return argument


def add_finding(argument: Argument, finding: BaseInput, executions: list, indexes: list) -> list:
    for index in indexes:
        if argument.multiple:
            executions[index].append(finding)
        else:
            execution_copy = [f for f in executions[index] if type(f) != type(finding)]
            if len(execution_copy) == len(executions[index]):
                executions[index].append(finding)
                break
            else:
                execution_copy.append(finding)
                executions.append(execution_copy)
                break
    return executions


def get_executions_from_findings(findings: list, tool: Tool) -> list:
    executions = [[]]
    finding_relations = utils.get_relations_between_input_types()
    for input_type, related_input_types in list(reversed(finding_relations.items())):
        argument = select_argument(tool, input_type)
        if not argument:
            continue
        filtered = [f for f in findings if (
            isinstance(f, input_type.get_related_model_class()) or
            isinstance(f, input_type.get_callback_target_class())
        )]
        if not filtered:
            continue
        relations = {}
        for relation in related_input_types:
            for index, exec_findings in enumerate(executions):
                for f in exec_findings:
                    if (
                        isinstance(f, relation.get_related_model_class()) or
                        isinstance(f, relation.get_callback_target_class())
                    ):
                        if index in relations:
                            relations[index]['findings'].append(f)
                        else:
                            relations[index] = {
                                'field': relation.name.lower(),
                                'findings': [f]
                            }
            if relations:
                break
        for finding in filtered:
            indexes = range(len(executions))
            if relations:
                related = [index for index, value in relations.items() if getattr(finding, value['field']) in value['findings']]
                if len(related) > 0:
                    indexes = related
            executions = add_finding(argument, finding, executions, indexes)
    return executions

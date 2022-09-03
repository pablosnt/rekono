from typing import Any, Dict, List, cast

from input_types import utils
from input_types.base import BaseInput
from input_types.models import InputType
from stringcase import snakecase
from tools.models import Argument, Input, Tool


def get_executions_with_relations(base_inputs: Dict[InputType, List[BaseInput]], tool: Tool) -> List[List[BaseInput]]:
    executions: List[List[BaseInput]] = [[]]                                    # BaseInput list for each execution
    # It's required because base inputs will be assigned to executions based on relationships between them
    input_relations = utils.get_relations_between_input_types()                 # Get relations between input types
    # For each input type, and his related input types
    for input_type, related_input_types in list(reversed(input_relations.items())):
        if input_type not in base_inputs:
            continue
        argument = Argument.objects.filter(tool=tool, inputs__type=input_type).order_by('inputs__order').first()
        if related_input_types:
            for base_input in base_inputs[input_type]:
                for index, execution_list in enumerate(executions.copy()):
                    assigned = False
                    for related_input_type in related_input_types:
                        base_inputs_by_class = [bi for bi in execution_list if bi.__class__ == base_input.__class__]
                        related_target = related_input_type.get_callback_target_class()
                        related_target_field = snakecase(cast(Any, related_target).__name__) if related_target else None
                        if (
                            (
                                hasattr(base_input, related_input_type.name.lower()) and
                                getattr(base_input, related_input_type.name.lower()) in execution_list
                            ) or
                            (
                                hasattr(base_input, related_target_field) and
                                getattr(base_input, related_target_field) in execution_list
                            )
                        ):
                            if argument.multiple or len(base_inputs_by_class) == 0:
                                executions[index].append(base_input)
                                assigned = True
                                break
                            elif not argument.multiple and len(base_inputs_by_class) > 0:
                                new_execution = execution_list.copy()
                                new_execution.remove(base_inputs_by_class[0])
                                new_execution.append(base_input)
                                executions.append(new_execution)
                                assigned = True
                                break
                    if assigned:
                        break
        elif argument.multiple:
            for item in range(len(executions)):
                executions[item].extend(base_inputs[input_type])
        else:
            new_executions: List[List[BaseInput]] = []
            for base_input in base_inputs[input_type]:
                for execution_list in executions:
                    new_executions.append(list(execution_list + [base_input]))
            executions = new_executions
    return executions


def get_executions_from_findings(base_inputs: List[BaseInput], tool: Tool) -> List[List[BaseInput]]:
    '''Get needed executions for a tool based on a given a input (Finding, Resource or Target) list.

    Args:
        base_inputs (List[BaseInput]): BaseInput list
        tool (Tool): Tool that will be executed

    Returns:
        List[List[BaseInput]]: List of inputs to be passed for each tool execution
    '''
    tool_inputs: List[Input] = Input.objects.filter(argument__tool=tool).all()
    filtered_base_inputs: Dict[InputType, List[BaseInput]] = {}
    for tool_input in tool_inputs:
        base_input_list = [
            bi for bi in base_inputs if bi.__class__ in [
                c for c in [tool_input.type.get_related_model_class(), tool_input.type.get_callback_target_class()] if c
            ]
        ]
        if base_input_list:
            filtered_base_inputs[tool_input.type] = base_input_list
    if len(filtered_base_inputs.keys()) > 1:
        return get_executions_with_relations(filtered_base_inputs, tool)
    elif len(filtered_base_inputs.keys()) == 1:
        argument = Argument.objects.filter(tool=tool, inputs__type=list(filtered_base_inputs.keys())[0]).first()
        if argument.multiple:
            return list(filtered_base_inputs.values())
        else:
            return cast(List[List[BaseInput]], [[bi] for bi in list(filtered_base_inputs.values())])
    return [base_inputs]

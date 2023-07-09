from typing import Any, Dict, List, cast

from input_types import utils
from input_types.base import BaseInput
from input_types.models import InputType
from stringcase import snakecase
from tools.models import Argument, Input, Tool


def get_executions_from_findings_with_relationships(
    base_inputs: Dict[InputType, List[BaseInput]],
    tool: Tool
) -> List[List[BaseInput]]:
    '''Get needed executions for a tool based on a given inputs with relationships between them.

    Args:
        base_inputs (Dict[InputType, List[BaseInput]]): InputTypes for this tool and related input list
        tool (Tool): Tool that will be executed

    Returns:
        List[List[BaseInput]]: List of inputs to be passed for each tool execution
    '''
    executions: List[List[BaseInput]] = [[]]                                    # BaseInput list for each execution
    # It's required because base inputs will be assigned to executions based on relationships between them
    input_relations = utils.get_relations_between_input_types()                 # Get relations between input types
    # For each input type, and his related input types
    for input_type, related_input_types in list(reversed(input_relations.items())):
        if input_type not in base_inputs:
            continue
        # Get argument by tool and input type
        argument = Argument.objects.filter(tool=tool, inputs__type=input_type).order_by('inputs__order').first()
        if related_input_types:                                                 # Input with related input types
            for base_input in base_inputs[input_type]:                          # For each input
                for index, execution_list in enumerate(executions.copy()):      # For each execution list
                    assigned = False
                    for related_input_type in related_input_types:              # For each related input type
                        # Check number of inputs of the same type in this execution
                        base_inputs_by_class = [bi for bi in execution_list if bi.__class__ == base_input.__class__]
                        # Get callback model class from related input type
                        callback_model = related_input_type.get_callback_model_class()
                        # Get field name to the related callback model
                        callback_model_field = snakecase(cast(Any, callback_model).__name__) if callback_model else ''
                        if (
                            (
                                # Check if input has a relationship
                                hasattr(base_input, related_input_type.name.lower()) and
                                getattr(base_input, related_input_type.name.lower()) in execution_list
                            ) or
                            (
                                # Check if input has a relationship with a callback model
                                hasattr(base_input, callback_model_field) and
                                getattr(base_input, callback_model_field) in execution_list
                            )
                        ):
                            if argument.multiple or len(base_inputs_by_class) == 0:
                                # Add input in current execution
                                executions[index].append(base_input)
                                assigned = True
                                break
                            elif not argument.multiple and len(base_inputs_by_class) > 0:
                                # Duplicate current execution
                                new_execution = execution_list.copy()           # Copy input list
                                new_execution.remove(base_inputs_by_class[0])   # Remove input with same type
                                new_execution.append(base_input)                # Add input
                                executions.append(new_execution)
                                assigned = True
                                break
                    if assigned:
                        break
        elif argument.multiple:
            # Input type without relationships and argument that allows multiple inputs
            for item in range(len(executions)):
                executions[item].extend(base_inputs[input_type])                # Add inputs in all executions
        else:                                                                   # Input type without relationships
            new_executions: List[List[BaseInput]] = []
            for base_input in base_inputs[input_type]:                          # For each input
                for execution_list in executions:                               # For each execution
                    new_executions.append(list(execution_list + [base_input]))  # Add input to the execution
            executions = new_executions
    return executions


def get_executions_from_findings(base_inputs: List[BaseInput], tool: Tool) -> List[List[BaseInput]]:
    '''Get needed executions for a tool based on a given input (Finding, Resource or Target) list.

    Args:
        base_inputs (List[BaseInput]): BaseInput list
        tool (Tool): Tool that will be executed

    Returns:
        List[List[BaseInput]]: List of inputs to be passed for each tool execution
    '''
    tool_inputs: List[Input] = Input.objects.filter(argument__tool=tool).all()  # Get inputs by tool
    filtered_base_inputs: Dict[InputType, List[BaseInput]] = {}
    for tool_input in tool_inputs:
        base_input_list = [
            bi for bi in base_inputs if bi.__class__ in [
                tool_input.type.get_model_class(), tool_input.type.get_callback_model_class()
            ]
        ]
        if base_input_list:
            filtered_base_inputs[tool_input.type] = base_input_list             # Relation between inputs and classes
    if len(filtered_base_inputs.keys()) > 1:                                    # Multiple input types
        # Get executions from inputs with maybe relationships
        return get_executions_from_findings_with_relationships(filtered_base_inputs, tool)
    elif len(filtered_base_inputs.keys()) == 1:                                 # Only one input type
        # Get argument by tool and input type
        argument = Argument.objects.filter(
            tool=tool, inputs__type=list(filtered_base_inputs.keys())[0]
        ).order_by('inputs__order').first()
        if argument.multiple:                                                   # Argument with multiple inputs
            return list(filtered_base_inputs.values())                          # One execution with all inputs
        else:
            return [[bi] for bi in list(filtered_base_inputs.values())[0]]      # One execution for each input
    # By default, one execution with all inputs
    return [base_inputs]

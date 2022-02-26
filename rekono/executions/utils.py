from typing import Any, Dict, List, cast

from input_types import utils
from input_types.base import BaseInput
from input_types.models import InputType
from stringcase import snakecase
from tools.models import Argument, Tool


def select_argument(tool: Tool, input_type: InputType) -> Argument:
    '''Select the properly argument for a tool and an input type.

    Args:
        tool (Tool): Tool to search the argument
        input_type (InputType): Input type to search the argument

    Returns:
        Argument: Selected argument
    '''
    # First, search argument with input order equals to 1
    argument = Argument.objects.filter(tool=tool, inputs__type=input_type, inputs__order=1).first()
    if not argument:
        # If not found, search first argument with input orger greater than 1
        argument = Argument.objects.filter(
            tool=tool, inputs__type=input_type, inputs__order__gt=1
        ).order_by('inputs__order').first()
    return argument


def get_related_executions(
    related_input_types: List[InputType],
    executions: List[List[BaseInput]]
) -> Dict[int, Dict[str, Any]]:
    '''Get executions with related input types.

    Args:
        related_input_types (List[InputType]): Related input types to search in the execution list
        executions (List[List[BaseInput]]):  List with the inputs already associated to each execution

    Returns:
        Dict[int, Dict[str, Any]]: Related executions data, including index, related field name and related inputs
    '''
    # Will save the executions (indexes) where the inputs can be assigned based on the related input types
    relations: Dict[int, Dict[str, Any]] = {}
    for relation in related_input_types:                                        # For each related input type
        for index, exec_inputs in enumerate(executions):                        # For each execution
            for i in exec_inputs:                                               # For each input assigned to execution
                related_model = relation.get_related_model_class()
                callback_target = relation.get_callback_target_class()
                target_field_name = snakecase(cast(Any, callback_target).__name__) if callback_target else None
                # Input related to the input type model
                is_model = isinstance(i, cast(Any, related_model)) if related_model else False
                # Input related to the input type target
                is_target = isinstance(i, cast(Any, callback_target)) if callback_target else False
                if is_model or is_target:
                    if index in relations:
                        relations[index]['findings'].append(i)                  # Add input to the relations
                    else:
                        relations[index] = {                                    # Create a new relation based on index
                            # Input field to access the related input
                            'field': relation.name.lower() if is_model else target_field_name,
                            'inputs': [i]                                       # Related input list
                        }
        if relations:
            break                                                               # Relations found
    return relations


def add_input(
    argument: Argument,
    base_input: BaseInput,
    executions: List[List[BaseInput]],
    indexes: List[int]
) -> List[List[BaseInput]]:
    '''Assign base input to the properly executions based on argument 'multiple' field.

    Args:
        argument (Argument): Argument related to the input type
        base_input (BaseInput): BaseInput. It can be a Finding, a Resource or a Target
        executions (List[List[BaseInput]]): List with the inputs already associated to each execution
        indexes (List[int]): Indexes of the executions list where the base input can be assigned

    Returns:
        List[List[BaseInput]]: Executions list after assign the base input
    '''
    for index in indexes:                                                       # For each selected index
        if argument.multiple:
            # Argument multiple is True, so input should be assigned in all selected executions (indexes)
            executions[index].append(base_input)
        else:
            # Argument multiple is False, so input should be assigned to executions without inputs of same type
            # Filter inputs in the current index, removing inputs of the same types
            execution_copy = [f for f in executions[index] if type(f) != type(base_input)]
            if len(execution_copy) == len(executions[index]):                   # No inputs of same type in this index
                executions[index].append(base_input)                            # Assign base input to the current index
            else:                                                               # Inputs with same type in this index
                # New execution is created from the filtered index and the input
                execution_copy.append(base_input)
                executions.append(execution_copy)
            # As argument multiple is False, base input only is assigned to one execution
            break
    return executions


def get_executions_from_findings(base_inputs: List[BaseInput], tool: Tool) -> List[List[BaseInput]]:
    '''Get needed executions for a tool based on a given a input (Finding, Resource or Target) list.

    Args:
        inputs (List[BaseInput]): BaseInput list
        tool (Tool): Tool that will be executed

    Returns:
        List[List[BaseInput]]: List of inputs to be passed for each tool execution
    '''
    executions: List[List[BaseInput]] = [[]]                                    # BaseInput list for each execution
    # It's required because base inputs will be assigned to executions based on relationships between them
    input_relations = utils.get_relations_between_input_types()                 # Get relations between input types
    # For each input type, and his related input types
    for input_type, related_input_types in list(reversed(input_relations.items())):
        argument = select_argument(tool, input_type)                            # Get properly argument for input type
        if not argument:
            continue                                                            # No argument found
        related_model = input_type.get_related_model_class()
        callback_target = input_type.get_callback_target_class()
        # Filter base inputs based on the input type model or target
        filtered = [f for f in base_inputs if (
            (related_model and isinstance(f, cast(Any, related_model))) or
            (callback_target and isinstance(f, cast(Any, callback_target)))
        )]
        if not filtered:
            continue                                                            # No base inputs found
        relations = get_related_executions(related_input_types, executions)     # Get executions with related inputs
        for base_input in filtered:                                             # For each base input
            # By default, can be assigned to all executions
            indexes = list(range(len(executions)))
            if relations:                                                       # If relations found
                # Filter relations to get indexes with related inputs to the current base input
                related = [i for i, v in relations.items() if getattr(base_input, v['field']) in v['inputs']]
                if len(related) > 0:                                            # Related inputs found
                    indexes = related
            executions = add_input(argument, base_input, executions, indexes)   # Assign base input to executions
    return executions

from typing import Any, Dict, List

from executions.models import Execution


def get_unique_filter(key_fields: List[Dict[str, Any]], fields: Dict[str, Any], execution: Execution) -> Dict[str, Any]:
    '''Get filter from finding data and its key fields.

    Args:
        key_fields (List[Dict[str, Any]]): Finding key fields
        fields (Dict[str, Any]): Finding fields and values
        execution (Execution): Execution where the finding is discovered

    Returns:
        Dict[str, Any]: Filter with the key fields and values
    '''
    base_field_found = False                                                    # Indicate if a base key field is found
    unique_filter: Dict[str, Any] = {}
    for field in key_fields:                                                    # For each key field
        value = fields.get(field['name'])                                       # Get value for the key field
        # Only one base key field should be included in the filter
        if value and (not base_field_found or not field.get('is_base')):
            unique_filter[field['name']] = value                                # Add key field and value to the filter
            if field.get('is_base'):
                base_field_found = True                                         # Update base indicator
    if not base_field_found and execution:                                      # If no base field found, use target
        unique_filter['execution__task__target'] = execution.task.target        # Add target value from execution
    return unique_filter

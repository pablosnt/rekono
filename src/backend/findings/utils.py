from typing import Any, Dict, List

from targets.models import Target


def get_unique_filter(key_fields: List[Dict[str, Any]], fields: Dict[str, Any], target: Target) -> Dict[str, Any]:
    '''Get filter from finding data and its key fields.

    Args:
        key_fields (List[Dict[str, Any]]): Finding key fields
        fields (Dict[str, Any]): Finding fields and values
        target (Target): Execution where the finding is discovered

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
    if not base_field_found and target:                                         # If no base field found, use target
        unique_filter['executions__task__target'] = target                      # Add target value
    return unique_filter

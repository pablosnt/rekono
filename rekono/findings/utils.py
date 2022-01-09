

from executions.models import Execution


def get_unique_filter(key_fields: list, fields: dict, execution: Execution) -> dict:
    base_field_found = False
    unique_filter = {}
    for field in key_fields:
        value = fields.get(field.get('name'))
        if value and (not base_field_found or not field.get('is_base')):
            unique_filter[field.get('name')] = value
            if field.get('is_base'):
                base_field_found = True
    if not base_field_found and execution:
        unique_filter['execution__task__target'] = execution.task.target
    return unique_filter

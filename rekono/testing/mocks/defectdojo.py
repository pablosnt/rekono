from typing import Any, Dict, Tuple

'''Mock for Defect-Dojo API integration implemented on defectdojo.api package.'''


def defect_dojo_success(*args: Any, **kwargs: Any) -> Tuple[bool, Dict[str, Any]]:
    '''Get mocked response for successfully Defect-Dojo operation.

    Returns:
        Tuple[bool, Dict[str, Any]]: Successfully Defect-Dojo response
    '''
    return True, {'id': 1, 'product': 1}


def defect_dojo_success_multiple(*args: Any, **kwargs: Any) -> Tuple[bool, Dict[str, Any]]:
    '''Get mocked response for successfully Defect-Dojo operation with results.

    Returns:
        Tuple[bool, Dict[str, Any]]: Successfully Defect-Dojo response
    '''
    return True, {'results': [{'id': 1, 'product': 1}]}


def defect_dojo_error(*args: Any, **kwargs: Any) -> Tuple[bool, Dict[str, Any]]:
    '''Get mocked response for invalid Defect-Dojo operation.

    Returns:
        Tuple[bool, Dict[str, Any]]: Generic error response
    '''
    return False, {'message': 'Generic Defect-Dojo error'}

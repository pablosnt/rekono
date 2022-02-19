from typing import Any, Dict, Tuple

'''Mock for Defect-Dojo API integration implemented on defectdojo.api package.'''


def get_product(*args: Any) -> Tuple[bool, Dict[str, Any]]:
    '''Get mocked response for get product by Id feature.

    Returns:
        Tuple[bool, Dict[str, Any]]: Success response
    '''
    return True, {}


def get_product_not_found(*args: Any) -> Tuple[bool, Dict[str, Any]]:
    '''Get mocked response for get product by Id feature.

    Returns:
        Tuple[bool, Dict[str, Any]]: Not found response
    '''
    return False, {'message': 'Product Id not found'}

from typing import Dict, List, Optional

import requests
from django.db import models
from input_types.base import BaseInput
from input_types.models import InputType


def get_url(host: str, port: int = None, endpoint: str = '', protocols: List[str] = ['http', 'https']) -> Optional[str]:
    '''Get a HTTP or HTTPS URL from host, port and endpoint.

    Args:
        host (str): Host to include in the URL
        port (int, optional): Port to include in the URL. Defaults to None.
        endpoint (str, optional): Endpoint to include in the URL. Defaults to ''.
        protocols (List[str], optional): Protocol list to check. Defaults to ['http', 'https'].

    Returns:
        Optional[str]: [description]
    '''
    schemas = ['{protocol}://{host}/{endpoint}']
    if port:
        schemas.append('{protocol}://{host}:{port}/{endpoint}')                 # Include port schema if port exists
    for url in schemas:                                                         # For each schema
        for protocol in protocols:                                              # For each protocol
            url_to_test = url.format(protocol=protocol, host=host, port=port, endpoint=endpoint)
            try:
                requests.get(url_to_test, timeout=5)                            # Test URL connection
                return url_to_test
            except Exception:
                continue
    return None


def get_relations_between_input_types() -> Dict[InputType, List[InputType]]:
    '''Get relations between the different input types.

    Returns:
        Dict[InputType, List[InputType]]: Dict with a list of related input types for each input type
    '''
    relations: Dict[InputType, List[InputType]] = {}
    input_types = InputType.objects.order_by('-id').all()                       # Get all input types
    for it in input_types:                                                      # For each input type
        relations[it] = []
        for field in it.get_related_model_class()._meta.get_fields():           # For each related model field
            # Check if field is a ForeignKey to a BaseInput model
            if isinstance(field, models.ForeignKey) and issubclass(field.related_model, BaseInput):
                # Found a related input type. Get 'related_model' reference from field metadata
                related_model = f'{field.related_model._meta.app_label}.{field.related_model._meta.model_name}'
                related_type = InputType.objects.get(related_model=related_model)   # Search InputType by related model
                relations[it].append(related_type)
    return relations

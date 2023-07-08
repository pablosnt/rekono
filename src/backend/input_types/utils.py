from typing import Dict, List, Optional

import requests
import urllib3
from django.db import models
from input_types.base import BaseInput
from input_types.models import InputType
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(category=InsecureRequestWarning)


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
    schema = '{protocol}://{host}/{endpoint}'
    if port:
        schema = '{protocol}://{host}:{port}/{endpoint}'                        # Include port schema if port exists
    for protocol in protocols:                                                  # For each protocol
        url_to_test = schema.format(protocol=protocol, host=host, port=port, endpoint=endpoint)
        try:
            # nosemgrep: python.requests.security.disabled-cert-validation.disabled-cert-validation
            requests.get(url_to_test, timeout=5, verify=False)                  # Test URL connection
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
    input_types = InputType.objects.filter(regular=True).order_by('-id').all()  # Get all input types
    for it in input_types:                                                      # For each input type
        relations[it] = []
        model = it.get_model_class()
        if model:
            for field in model._meta.get_fields():                              # For each model field
                # Check if field is a ForeignKey to a BaseInput model
                if field.__class__ == models.ForeignKey and issubclass(field.related_model, BaseInput):
                    # Search InputType by model
                    related_type = InputType.objects.filter(
                        model=f'{field.related_model._meta.app_label}.{field.related_model._meta.model_name}'
                    )
                    if related_type.exists():
                        relations[it].append(related_type.first())
    return relations

from typing import Optional

import requests
from django.apps import apps
from django.db import models
from input_types.base import BaseInput
from input_types.models import InputType


def get_url(host: str, port: int = 0, endpoint: str = '', https: bool = None) -> Optional[str]:
    protocols = ['http', 'https']
    if https is not None:
        protocols = ['https'] if https else ['http']
    for url in ['{protocol}://{host}:{port}/{endpoint}', '{protocol}://{host}/{endpoint}']:
        for protocol in protocols:
            url_to_test = url.format(protocol=protocol, host=host, port=port, endpoint=endpoint)
            if check_connection(url_to_test):
                return url_to_test


def check_connection(url: str) -> bool:
    try:
        requests.get(url, timeout=5)
        return True
    except Exception as ex:
        return False


def get_relations_between_input_types() -> dict:
    relations = {}
    input_types = InputType.objects.order_by('-id').all()
    for it in input_types:
        app_label, model_name = it.related_model.split('.', 1)
        model = apps.get_model(app_label=app_label, model_name=model_name)
        relations[it] = []
        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey) and issubclass(field.related_model, BaseInput):
                related_model = f'{field.related_model._meta.app_label}.{field.related_model._meta.model_name}'
                related_type = InputType.objects.get(related_model=related_model)
                relations[it].append(related_type)
    return relations

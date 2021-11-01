from typing import Any

import requests
from defectdojo.api import utils

from rekono.settings import DEFECT_DOJO as config


def create_endpoint(product: int, endpoint: Any) -> None:
    data = endpoint.defect_dojo()
    data.update({
        'product': product,
        'tags': config.get('TAGS') 
    })
    requests.post(utils.urls.get('endpoints'), headers=utils.headers, data=data)


def create_finding(test: int, finding: Any) -> None:
    data = finding.defect_dojo()
    data.update({
        'test': test,
        'tags': config.get('TAGS')
    })
    requests.post(utils.urls.get('findings'), headers=utils.headers, data=data)

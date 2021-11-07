from typing import Any

import requests
from defectdojo.api import utils
from findings.enums import Severity

from rekono.settings import DEFECT_DOJO as config

numerical_severity_mapping = {
    Severity.INFO.value: 'S0',
    Severity.LOW.value: 'S1',
    Severity.MEDIUM.value: 'S3',
    Severity.HIGH.value: 'S4',
    Severity.CRITICAL.value: 'S5',
}


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
        'tags': config.get('TAGS'),
        'numerical_severity': numerical_severity_mapping[data.get('severity')]
    })
    requests.post(utils.urls.get('findings'), headers=utils.headers, data=data)

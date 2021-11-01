from datetime import datetime

import requests
from defectdojo.api import utils

from rekono.settings import DEFECT_DOJO as config


def get_test_type() -> int:
    response = requests.get(
        f'{utils.urls.get("test_types")}?name={config.get("TEST_TYPE")}',
        headers=utils.headers
    )
    result = response.json()
    if result and len(result.get('results')) == 1:
        return result.get('results')[0].get('id')


def create_test_type() -> int:
    data = {
        'tags': config.get('TAGS'),
        'name': config.get("TEST_TYPE"),
        'dynamic_tool': True
    }
    response = requests.post(utils.urls.get("test_types"), headers=utils.headers, data=data)
    result = response.json()
    if result:
        return result.get('id')


def create_rekono_test(engagement_id: int) -> int:
    test_type_id = get_test_type()
    if not test_type_id:
        test_type_id = create_test_type()
    data = {
        'engagement': engagement_id,
        'tags': config.get('TAGS'),
        'title': config.get("TEST"),
        'description': config.get("TEST"),
        'target_start': datetime.now().strftime('%Y-%m-%d'),
        'target_end': datetime.now().strftime('%Y-%m-%d'),
        'test_type': test_type_id
    }
    response = requests.post(f'{utils.urls.get("tests")}', headers=utils.headers, data=data)
    result = response.json()
    if result:
        return result.get('id')

from datetime import datetime, timedelta

import requests
from defectdojo.api import utils

from rekono.settings import DEFECT_DOJO as config


def create_new_engagement(product_id: int, name: str, description: str) -> int:
    start = datetime.now()
    end = start + timedelta(days=7)
    data = {
        'tags': config.get('TAGS'),
        'name': name,
        'description': description,
        'product': product_id,
        'status': 'In Progress',
        'engagement_type': 'Interactive',
        'target_start': start.strftime('%Y-%m-%d'),
        'target_end': end.strftime('%Y-%m-%d'),
    }
    response = requests.post(utils.urls.get('engagements'), headers=utils.headers, data=data)
    result = response.json()
    if result:
        return result.get('id')


def check_engagement(engagement_id: int, product_id: int = None) -> tuple:
    if product_id:
        response = requests.get(
            f'{utils.urls.get("engagements")}?id={engagement_id}&product={product_id}',
            headers=utils.headers
        )
        result = response.json()
        if result and len(result.get('results')) > 0:
            return product_id, engagement_id
    else:
        response = requests.get(
            f'{utils.urls.get("engagements")}{engagement_id}/',
            headers=utils.headers
        )
        if response.status_code == 200:
            result = response.json()
            if result:
                return result.get('product')
    return None, None

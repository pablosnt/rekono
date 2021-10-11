import requests
from rekono.settings import DEFECT_DOJO as config
from integrations.defect_dojo.api import utils
from datetime import datetime, timedelta


def create_new_engagement(product_id: int) -> int:
    start = datetime.now()
    end = start + timedelta(days=7)
    data = {
        'tags': config.get('REKONO_TAGS'),
        'name': config.get('REKONO_ENGAGEMENT'),
        'description': config.get('REKONO_ENGAGEMENT'),
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


def get_rekono_engagement(product_id: int) -> int:
    engagement = config.get('REKONO_ENGAGEMENT')
    if not engagement:
        return None
    response = requests.get(
        f'{utils.urls.get("engagements")}?name={engagement}&product={product_id}',
        headers=utils.headers
    )
    results = response.json().get('results')
    if results:
        return results[0].get('id')
    return create_new_engagement(product_id)

import requests
from defectdojo.api import utils
from projects.models import Project

from rekono.settings import DEFECT_DOJO as config


def get_rekono_prod_type_id() -> int:
    prod_type_name = config.get('PROD_TYPE')
    response = requests.get(
        f'{utils.urls.get("prod_types")}?name={prod_type_name}',
        headers=utils.headers
    )
    if response.status_code == 200:
        results = response.json().get('results')
        if results:
            return results[0].get('id')


def create_rekono_prod_type() -> int:
    prod_type = config.get('PROD_TYPE')
    data = {
        'name': prod_type,
        'description': prod_type,
    }
    response = requests.post(utils.urls.get('prod_types'), headers=utils.headers, data=data)
    if response.status_code == 201:
        return response.json().get('id')


def check_product_id(id: int) -> bool:
    response = requests.get(
        f'{utils.urls.get("products")}{id}/',
        headers=utils.headers
    )
    return response.status_code == 200


def create_new_product(project: Project) -> int:
    prod_type_id = get_rekono_prod_type_id()
    if not prod_type_id:
        prod_type_id = create_rekono_prod_type()
    data = {
        'tags': config.get('TAGS'),
        'name': project.name,
        'description': project.description,
        'prod_type': prod_type_id,
    }
    response = requests.post(utils.urls.get('products'), headers=utils.headers, data=data)
    if response.status_code == 201:
        return response.json().get('id')

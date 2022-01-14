from datetime import datetime, timedelta

import requests
from defectdojo.constants import DD_DATE_FORMAT, DD_DATETIME_FORMAT
from executions.models import Execution
from findings.enums import Severity
from findings.models import Endpoint, Finding
from projects.models import Project
from tools.models import Tool

from rekono.settings import DEFECT_DOJO as config

SEVERITY_MAPPING = {
    Severity.INFO.value: 'S0',
    Severity.LOW.value: 'S1',
    Severity.MEDIUM.value: 'S3',
    Severity.HIGH.value: 'S4',
    Severity.CRITICAL.value: 'S5',
}


class DefectDojo:

    def __init__(self):
        self.url = f'{config.get("HOST")}/api/v2'
        self.api_key = config.get('API_KEY')
        self.tags = config.get('TAGS')
        self.product_auto_creation = config.get('PRODUCT_AUTO_CREATION')
        self.product_type = config.get('PRODUCT_TYPE')
        self.test_type = config.get('TEST_TYPE')
        self.test = config.get('TEST')

    def _request(
        self,
        method: str,
        url: str,
        params: dict = None,
        data: dict = None,
        files: dict = None,
        expected_status: int = 200
    ) -> tuple:
        headers = {
            'User-Agent': 'Rekono',
            'Authorization': f'Token {self.api_key}'
        }
        response = requests.request(
            method=method,
            url=f'{self.url}{url}',
            headers=headers,
            params=params,
            data=data,
            files=files,
            verify=False
        )
        if response.status_code == expected_status:
            return True, response.json()
        else:
            return False, response

    def get_rekono_product_type(self) -> tuple:
        params = {'name': self.product_type}
        return self._request('GET', '/product_types/', params=params)

    def create_rekono_product_type(self: int) -> tuple:
        data = {'name': self.product_type, 'description': self.product_type}
        return self._request('POST', '/product_types/', data=data, expected_status=201)

    def get_product(self, id: int) -> tuple:
        return self._request('GET', f'/products/{id}/')

    def create_product(self, product_type: int, project: Project) -> tuple:
        data = {
            'tags': self.tags,
            'name': project.name,
            'description': project.description,
            'prod_type': product_type
        }
        return self._request('POST', '/products/', data=data, expected_status=201)

    def get_engagement(self, id: int) -> tuple:
        return self._request('GET', f'/engagements/{id}/')

    def get_last_engagement(self, product: int, name: str) -> tuple:
        params = {'name': name, 'product': product, 'o': '-created'}
        return self._request('GET', '/engagements/', params=params)

    def create_engagement(self, product: int, name: str, description: str) -> tuple:
        start = datetime.now()
        end = start + timedelta(days=7)
        data = {
            'name': name,
            'description': description,
            'tags': self.tags,
            'product': product,
            'status': 'In Progress',
            'engagement_type': 'Interactive',
            'target_start': start.strftime(DD_DATE_FORMAT),
            'target_end': end.strftime(DD_DATE_FORMAT),
        }
        return self._request('POST', '/engagements/', data=data, expected_status=201)

    def get_rekono_test_type(self) -> tuple:
        params = {'name': self.test_type}
        return self._request('GET', '/test_types/', params=params)

    def create_rekono_test_type(self) -> tuple:
        data = {
            'name': self.test_type,
            'tags': self.tags,
            'dynamic_tool': True
        }
        return self._request('POST', '/test_types/', data=data, expected_status=201)

    def create_rekono_test(self, test_type: int, engagement: int) -> tuple:
        data = {
            'engagement': engagement,
            'test_type': test_type,
            'title': self.test,
            'description': self.test,
            'target_start': datetime.now().strftime(DD_DATETIME_FORMAT),
            'target_end': datetime.now().strftime(DD_DATETIME_FORMAT)
        }
        return self._request('POST', '/tests/', data=data, expected_status=201)

    def create_endpoint(self, product: int, endpoint: Endpoint) -> tuple:
        data = endpoint.defect_dojo()
        data.update({'product': product})
        return self._request('POST', '/endpoints/', data=data, expected_status=201)

    def create_finding(self, test: int, finding: Finding) -> tuple:
        data = finding.defect_dojo()
        data.update({
            'test': test,
            'numerical_severity': SEVERITY_MAPPING[data.get('severity')],
            'active': True
        })
        return self._request('POST', '/findings/', data=data, expected_status=201)

    def import_scan(self, engagement: int, execution: Execution, tool: Tool) -> tuple:
        data = {
            'scan_type': tool.defectdojo_scan_type,
            'engagement': engagement,
            'tags': self.tags
        }
        files = {
            'file': open(execution.output_file, 'r')
        }
        return self._request('POST', '/import-scan/', data=data, files=files, expected_status=201)

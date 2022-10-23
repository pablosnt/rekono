import logging
from datetime import datetime, timedelta
from typing import Any, Tuple
from urllib.parse import urlparse

import requests
from findings.enums import Severity
from projects.models import Project
from requests.adapters import HTTPAdapter, Retry
from system.models import System

from defectdojo.constants import DD_DATE_FORMAT, DD_DATETIME_FORMAT

# Mapping between Rekono and Defect-Dojo severities
SEVERITY_MAPPING = {
    str(Severity.INFO): 'S0',
    str(Severity.LOW): 'S1',
    str(Severity.MEDIUM): 'S3',
    str(Severity.HIGH): 'S4',
    str(Severity.CRITICAL): 'S5',
}

logger = logging.getLogger()                                                    # Rekono logger


class DefectDojo:
    '''Defect-Dojo API handler to allow Rekono integration.'''

    def __init__(self):
        '''Defect-Dojo API constructor.'''
        self.system = None
        self.http_session = None

    def get_system(self) -> System:
        '''Get system settings instance.

        Returns:
            System: System settings
        '''
        if not self.system:
            self.system = System.objects.first()
        return self.system

    def get_http_session(self) -> requests.Session:
        '''Get HTTP session configured to retry requests after unexpected errors.

        Returns:
            requests.Session: HTTP session properly configured
        '''
        if not self.http_session:
            schema = urlparse(self.get_system().defect_dojo_url).scheme         # Get API schema
            # Configure retry protocol to prevent unexpected errors
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504, 599])
            self.http_session = requests.Session()
            self.http_session.mount(f'{schema}://', HTTPAdapter(max_retries=retries))
        return self.http_session

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        data: dict = None,
        files: dict = None,
        expected_status: int = 200
    ) -> Tuple[bool, Any]:
        '''Perform a Defect-Dojo API request.

        Args:
            method (str): HTTP method to use
            endpoint (str): Endpoint to call
            params (dict, optional): Query params to include in the request. Defaults to None.
            data (dict, optional): Body data to include in the request. Defaults to None.
            files (dict, optional): Files to include in the request. Defaults to None.
            expected_status (int, optional): Expected HTTP response status. Defaults to 200.

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        system = self.get_system()
        headers = {
            'User-Agent': 'Rekono',                                             # Rekono User-Agent
            'Authorization': f'Token {system.defect_dojo_api_key}'              # Authentication via API key
        }
        try:
            response = self.get_http_session().request(                         # Defect-Dojo API request
                method=method,
                url=f'{system.defect_dojo_url}/api/v2{endpoint}',
                headers=headers,
                params=params,
                data=data,
                files=files,
                verify=system.defect_dojo_verify_tls
            )
        except requests.exceptions.ConnectionError:
            response = self.get_http_session().request(                         # Defect-Dojo API request
                method=method,
                url=f'{system.defect_dojo_url}/api/v2{endpoint}',
                headers=headers,
                params=params,
                data=data,
                files=files,
                verify=system.defect_dojo_verify_tls
            )
        logger.info(f'[Defect-Dojo] {method.upper()} /api/v2{endpoint} > HTTP {response.status_code}')
        if response.status_code == expected_status:
            return True, response.json()                                        # Successful request
        else:
            return False, response                                              # Failed request

    def is_available(self) -> bool:
        '''Check if Defect-Dojo integration is available.

        Returns:
            bool: Indicate if Defect-Dojo integration is available or not
        '''
        if not self.get_system().defect_dojo_url:
            return False
        try:
            success, _ = self.request('get', '/test_types/', params={'limit': 1})
        except requests.exceptions.ConnectionError:
            success = False
        if not success:
            logger.error('[Defect-Dojo] Integration with Defect-Dojo is not available')
        return success

    def get_rekono_product_type(self) -> Tuple[bool, dict]:
        '''Get product type associated to Rekono, based on configurated name.

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        return self.request('GET', '/product_types/', params={'name': self.get_system().defect_dojo_product_type})

    def create_rekono_product_type(self) -> Tuple[bool, dict]:
        '''Create new product type associated to Rekono, based on configurated name.

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        system = self.get_system()
        data = {'name': system.defect_dojo_product_type, 'description': system.defect_dojo_product_type}
        return self.request('POST', '/product_types/', data=data, expected_status=201)

    def get_product(self, id: int) -> Tuple[bool, dict]:
        '''Get product by Id.

        Args:
            id (int): Product Id to get

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        return self.request('GET', f'/products/{id}/')

    def create_product(self, product_type: int, project: Project) -> Tuple[bool, dict]:
        '''Create new Defect-Dojo product from Rekono project.

        Args:
            product_type (int): Product type associated to the product
            project (Project): Rekono project to create in Defect-Dojo as product

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        data = {
            'tags': [self.get_system().defect_dojo_tag],                        # Includes the configurated tag
            'name': project.name,
            'description': project.description,
            'prod_type': product_type
        }
        return self.request('POST', '/products/', data=data, expected_status=201)

    def get_engagement(self, id: int) -> Tuple[bool, dict]:
        '''Get engagement by Id.

        Args:
            id (int): Engagement Id to get

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        return self.request('GET', f'/engagements/{id}/')

    def create_engagement(self, product: int, name: str, description: str) -> Tuple[bool, dict]:
        '''Create new engagement.

        Args:
            product (int): Product Id where the engagement will be created
            name (str): Engagement name
            description (str): Engagement description

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        start = datetime.now()
        end = start + timedelta(days=7)                                         # End date after 7 days
        data = {
            'name': name,
            'description': description,
            'tags': [self.get_system().defect_dojo_tag],                        # Includes the configurated tag
            'product': product,
            'status': 'In Progress',
            'engagement_type': 'Interactive',                                   # The other option is 'CI/CD'
            'target_start': start.strftime(DD_DATE_FORMAT),
            'target_end': end.strftime(DD_DATE_FORMAT),
        }
        return self.request('POST', '/engagements/', data=data, expected_status=201)

    def get_rekono_test_type(self) -> Tuple[bool, dict]:
        '''Get test type associated to Rekono, based on configurated name.

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        return self.request('GET', '/test_types/', params={'name': self.get_system().defect_dojo_test_type})

    def create_rekono_test_type(self) -> Tuple[bool, dict]:
        '''Create new test type associated to Rekono, based on configurated name.

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        system = self.get_system()
        data = {
            'name': system.defect_dojo_test_type,
            'tags': [system.defect_dojo_tag],                                   # Includes the configurated tag
            'dynamic_tool': True                                                # Cause most Rekono tools are dynamic
        }
        return self.request('POST', '/test_types/', data=data, expected_status=201)

    def create_rekono_test(self, test_type: int, engagement: int) -> Tuple[bool, dict]:
        '''Create new Rekono test.

        Args:
            test_type (int): Test type Id associated to the test
            engagement (int): Engagement Id where the test will be created

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        system = self.get_system()
        data = {
            'engagement': engagement,
            'test_type': test_type,
            'title': system.defect_dojo_test,
            'description': system.defect_dojo_test,
            'target_start': datetime.now().strftime(DD_DATETIME_FORMAT),
            'target_end': datetime.now().strftime(DD_DATETIME_FORMAT)           # Because the test is completed
        }
        return self.request('POST', '/tests/', data=data, expected_status=201)

    def create_endpoint(self, product: int, endpoint: Any) -> Tuple[bool, dict]:
        '''Create new Defect-Dojo endpoint from Rekono endpoint.

        Args:
            product (int): Product Id where the endpoint will be created
            endpoint (Path): Rekono endpoint to create in Defect-Dojo

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        data = endpoint.defect_dojo()
        data.update({'product': product})
        return self.request('POST', '/endpoints/', data=data, expected_status=201)

    def create_finding(self, test: int, finding: Any) -> Tuple[bool, dict]:
        '''Create new Defect-Dojo finding from Rekono finding.

        Args:
            test (int): Test Id where the finding will be created
            finding (Finding): Rekono finding to create in Defect-Dojo

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        data = finding.defect_dojo()
        data.update({
            'test': test,
            'numerical_severity': SEVERITY_MAPPING[data.get('severity')],       # Mapping between severity values
            'active': True                                                      # Always created as active
        })
        return self.request('POST', '/findings/', data=data, expected_status=201)

    def import_scan(self, engagement: int, execution: Any) -> Tuple[bool, dict]:
        '''Import Rekono execution output in Defect-Dojo.

        Args:
            engagement (int): Engagement Id where the scan will be imported
            execution (Execution): Completed Rekono execution to import in Defect-Dojo

        Returns:
            Tuple[bool, dict]: Indicates if request was successful or not (bool), and return the response body (dict)
        '''
        data = {
            # https://defectdojo.github.io/django-DefectDojo/integrations/parsers/
            'scan_type': execution.tool.defectdojo_scan_type,
            'engagement': engagement,
            'tags': [self.get_system().defect_dojo_tag]                         # Includes the configurated tag
        }
        files = {
            'file': open(execution.output_file, 'r')                            # Execution output file
        }
        return self.request('POST', '/import-scan/', data=data, files=files, expected_status=201)

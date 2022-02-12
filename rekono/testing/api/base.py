import json
import os
from typing import Any, Callable, Dict, List

from django.http import HttpResponse
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User


class RekonoTestCase(TestCase):
    '''Base test case.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.current_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')         # Testing path
        self.login = '/api/token/'                                              # Login endpoint
        self.username = 'rekono'                                                # Username for test authentication
        self.email = 'rekono@rekono.rekono'                                     # Email for test authentication
        self.password = 'rekono'                                                # Password for test authentication
        # Create user for test authentication
        self.admin = User.objects.create_superuser(self.username, self.email, self.password)
        data = {'username': self.username, 'password': self.password}           # Login data
        content = self.api_test(APIClient().post, self.login, 200, data, {})    # Login request
        self.rekono = APIClient(HTTP_AUTHORIZATION=f'Bearer {content.get("access")}')   # Configure Rekono API client

    def get_content(self, response: HttpResponse) -> Dict[Any, Any]:
        '''Get content from HTTP response.

        Args:
            response (HttpResponse): HTTP response

        Returns:
            Dict[Any, Any]: Response content
        '''
        return json.loads(response.content.decode('utf-8')) if response.content else {}

    def check_fields(self, fields: List[str], content: Dict[str, Any], expected: Dict[str, Any]) -> None:
        '''Check expected values for some response fields.

        Args:
            fields (List[str]): List of field names
            content (Dict[str, Any]): Response content
            expected (Dict[str, Any]): Expected data
        '''
        for field in fields:
            self.assertEqual(content[field], expected[field])

    def api_test(
        self,
        request: Callable,
        endpoint: str,
        expected_status: int,
        data: Dict[str, Any] = {},
        expected: Dict[str, Any] = {},
        format: str = 'json'
    ) -> Dict[Any, Any]:
        '''Test Rekono API.

        Args:
            request (Callable): Method to make Rekono API request
            endpoint (str): Rekono API endpoint
            expected_status (int): Expected HTTP status code
            data (Dict[str, Any], optional): Request body. Defaults to {}.
            expected (Dict[str, Any], optional): Expected response content. Defaults to {}.
            format (str, optional): Request body format. Defaults to json.

        Returns:
            Dict[Any, Any]: Response content
        '''
        if data:                                                                # HTTP body
            response = request(endpoint, data=data, format=format)              # Make Rekono API request
        else:                                                                   # No HTTP body
            response = request(endpoint)                                        # Make Rekono API request
        self.assertEqual(response.status_code, expected_status)                 # Check HTTP status code
        content = self.get_content(response)                                    # Get content from HTTP response
        if expected:                                                            # Expected response content
            self.check_fields(list(expected.keys()), content, expected)         # Check expected data
        return content

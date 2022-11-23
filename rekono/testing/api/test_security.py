from typing import Callable, cast

from django.forms import ValidationError
from security.csp_header import admin, redoc, swagger
from security.input_validation import (validate_name, validate_number,
                                       validate_text, validate_time_amount)
from security.passwords import PasswordComplexityValidator
from testing.api.base import RekonoApiTestCase


class SecurityTest(RekonoApiTestCase):
    '''Test cases for Security module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        # Mapping between endpoints and CSP headersa
        self.csp_mapping = [('/admin/', admin), ('/api/schema/swagger-ui.html', swagger), ('/api/schema/redoc/', redoc)]
        # Data for testing
        self.invalid_passwords = [
            'ABCDEF123456.',                                                    # Lower case required
            'abcdef123456.',                                                    # Upper case required
            'ABCDEFabcdef.',                                                    # Digits required
            'ABCDEFabcdef1',                                                    # Symbols required
        ]
        self.input_validation_data = [
            ('invalid#name#', validate_name, False),
            ('validname', validate_name, True),
            ('invalid;text;', validate_text, False),
            ('valid#text#', validate_text, True),
            (0, validate_number, False),
            (1000000, validate_number, False),
            (1, validate_number, True),
            (999999, validate_number, True),
            (0, validate_time_amount, False),
            (1001, validate_time_amount, False),
            (1, validate_time_amount, True),
            (1000, validate_time_amount, True),
        ]

    def test_logout(self) -> None:
        '''Test logout feature.'''
        self.api_test(self.client.post, '/api/logout/', data={'refresh_token': self.refresh})       # Logout
        # Try to refresh access token
        self.api_test(self.client.post, '/api/token/refresh/', 401, data={'refresh': self.refresh})

    def test_invalid_logout(self) -> None:
        '''Test logout feature with invalid data.'''
        self.api_test(self.client.post, '/api/logout/', 400)                    # Refresh token is required

    def test_csp_header_selection(self) -> None:
        '''Test CSP header value by endpoint.'''
        for endpoint, csp in self.csp_mapping:
            response = self.unauthn_client.get(endpoint)                        # Request to endpoint
            self.assertEqual(csp, response.headers['Content-Security-Policy'])  # Check CSP in the response headers

    def test_invalid_password_policy(self) -> None:
        '''Test password policy.'''
        validator = PasswordComplexityValidator()                               # Password validator
        self.assertEqual(validator.message, validator.get_help_text())
        for password in self.invalid_passwords:
            invalid_password = False
            try:
                validator.validate(password)                                    # Password validation
            except ValidationError:
                invalid_password = True
            self.assertTrue(invalid_password)                                   # Check invalid password

    def test_input_validation(self) -> None:
        '''Test input validation countermeasure.'''
        for value, validator, expected in self.input_validation_data:
            valid = True
            try:
                cast(Callable, validator)(value)                                # Input validation
            except ValidationError:
                valid = False
            self.assertEqual(expected, valid)                                   # Check expected conclusion

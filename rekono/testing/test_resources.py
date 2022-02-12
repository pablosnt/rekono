import os
from typing import Any, Dict

from testing.base import RekonoTestCase


class WordlistsTest(RekonoTestCase):
    '''Test cases for Wordlist entity from Resources module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.endpoint = '/api/resources/wordlists/'                             # Wordlists API endpoint
        # Wordlists paths
        self.passwords = os.path.join(self.current_path, 'data', 'resources', 'passwords.txt')
        self.endpoints = os.path.join(self.current_path, 'data', 'resources', 'endpoints.txt')
        # Data for testing
        self.name = 'ZZZ'
        self.fields = ['name', 'type', 'size', 'size', 'creator']               # Fields to check
        self.wordlist = self.create_passwords_wordlist(self.name)               # Create wordlist for testing

    def create_wordlist(self, name: str, path: str, type: str, status_code: int) -> Dict[str, Any]:
        '''Create wordlist and check response.

        Args:
            name (str): Wordlist name
            path (str): Wordlist filepath
            type (str): Wordlist type
            status_code (int): Expected HTTP status code

        Returns:
            Dict[str, Any]: Created wordlist data
        '''
        with open(path, 'r') as file:
            data = {'name': name, 'type': type, 'file': file}
            expected = {'name': name, 'type': type, 'size': 3}
            if status_code == 201:
                # Create wordlist and check response. Expected successfull request
                return self.api_test(self.rekono.post, self.endpoint, status_code, data, expected, 'multipart')
            else:
                # Try to create wordlist
                return self.api_test(self.rekono.post, self.endpoint, status_code, data, {}, 'multipart')

    def create_passwords_wordlist(self, name: str, status_code: int = 201) -> Dict[str, Any]:
        '''Create wordlist of type Password.

        Args:
            name (str): Wordlist name
            status_code (int, optional): Expected HTTP status code. Defaults to 201.

        Returns:
            Dict[str, Any]: Created wordlist data
        '''
        return self.create_wordlist(name, self.passwords, 'Password', status_code)

    def create_endpoints_wordlist(self, name: str, status_code: int = 201) -> Dict[str, Any]:
        '''Create wordlist of type Endpoint.

        Args:
            name (str): Wordlist name
            status_code (int, optional): Expected HTTP status code. Defaults to 201.

        Returns:
            Dict[str, Any]: Created wordlist data
        '''
        return self.create_wordlist(name, self.endpoints, 'Endpoint', status_code)

    def test_create(self) -> None:
        '''Test wordlist creation feature.'''
        new_wordlist = self.create_endpoints_wordlist(self.name + self.name)    # Create new wordlist
        content = self.api_test(self.rekono.get, '/api/resources/wordlists/?o=-name', 200)          # Get all wordlists
        # Check that the first one is the new wordlist
        self.check_fields(self.fields, content['results'][0], new_wordlist)

    def test_invalid_create(self) -> None:
        '''Test wordlist creation feature with invalid data.'''
        self.create_endpoints_wordlist(self.name, 400)                          # Wordlist already exists

    def test_update(self) -> None:
        '''Test wordlist update feature.'''
        with open(self.endpoints, 'r') as wordlist:
            data = {'name': self.name, 'type': 'Endpoint', 'file': wordlist}
            expected = {'name': data['name'], 'type': data['type'], 'size': 3}
            updated = self.api_test(                                            # Update wordlist
                self.rekono.put, f'{self.endpoint}{self.wordlist["id"]}/', 200,
                data, expected, 'multipart'
            )
        # Check the updated wordlist data
        self.api_test(self.rekono.get, f'/api/resources/wordlists/{self.wordlist["id"]}/', 200, {}, updated)

    def test_invalid_update(self) -> None:
        '''Test wordlist update feature with invalid data.'''
        new_wordlist = self.create_passwords_wordlist(self.name + self.name)    # Create new wordlist
        with open(self.passwords, 'r') as wordlist:
            data = {'name': new_wordlist['name'], 'type': 'Password', 'file': wordlist}
            # Wordlist name already exists
            self.api_test(self.rekono.put, f'{self.endpoint}{self.wordlist["id"]}/', 400, data, {}, 'multipart')

    def test_delete(self) -> None:
        '''Test wordlist deletion feature.'''
        before = self.api_test(self.rekono.get, f'{self.endpoint}?o=-name', 200)                    # Get wordlists
        # Delete testing wordlist
        self.api_test(self.rekono.delete, f'{self.endpoint}{self.wordlist["id"]}/', 204, {})
        self.api_test(self.rekono.get, f'{self.endpoint}?o=-name', 200, {}, {'count': before['count'] - 1})

    def test_like_dislike(self) -> None:
        '''Test like and dislike features for wordlists.'''
        # Like testing wordlist
        self.api_test(self.rekono.post, f'{self.endpoint}{self.wordlist["id"]}/like/', 201)
        self.api_test(self.rekono.get, f'{self.endpoint}{self.wordlist["id"]}/', 200, {}, {'liked': True, 'likes': 1})
        # Dislike testing wordlist
        self.api_test(self.rekono.post, f'{self.endpoint}{self.wordlist["id"]}/dislike/', 204)
        self.api_test(self.rekono.get, f'{self.endpoint}{self.wordlist["id"]}/', 200, {}, {'liked': False, 'likes': 0})

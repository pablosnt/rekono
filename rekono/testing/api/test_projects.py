from testing.api.test_base import RekonoTestCase


class ProjectsTest(RekonoTestCase):
    '''Test cases for Projects module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        self.endpoint = '/api/projects/'                                        # Projects API endpoint
        super().setUp()
        # Data for testing
        self.used_data = {'name': self.project.name, 'description': self.project.description, 'tags': self.project.tags}
        self.new_data = {'name': 'New Test', 'description': 'New Test', 'tags': ['new']}
        self.models = {self.project: self.project.name}                         # Models to test __str__ method

    def test_create(self) -> None:
        '''Test project creation feature.'''
        # Create new project
        self.api_test(self.client.post, self.endpoint, 201, data=self.new_data, expected=self.new_data)

    def test_invalid_create(self) -> None:
        '''Test project creation feature with invalid data.'''
        self.api_test(self.client.post, self.endpoint, 400, data=self.used_data)    # Project already exists

    def test_update(self) -> None:
        '''Test project update feature.'''
        # Update project
        self.api_test(self.client.put, f'{self.endpoint}{self.project.id}/', data=self.new_data, expected=self.new_data)

    def test_invalid_update(self) -> None:
        '''Test project update feature with invalid data.'''
        # Create new project
        content = self.api_test(self.client.post, self.endpoint, 201, data=self.new_data, expected=self.new_data)
        # Project already exists
        self.api_test(self.client.put, f'{self.endpoint}{content["id"]}/', 400, data=self.used_data)

    def test_delete(self) -> None:
        '''Test project deletion feature.'''
        self.api_test(self.client.delete, f'{self.endpoint}{self.project.id}/', 204)                # Delete new project
        self.api_test(self.client.get, f'{self.endpoint}{self.project.id}/', 404)

    def test_add_member(self) -> None:
        '''Test add project member feature.'''
        # Add member to the testing project
        self.api_test(self.client.post, f'{self.endpoint}{self.project.id}/members/', 201, data={'user': self.other.id})

    def test_add_not_found_member(self) -> None:
        '''Test add project member feature with not found user.'''
        # Add unexisting member to the testing project
        self.api_test(self.client.post, f'{self.endpoint}{self.project.id}/members/', 404, data={'user': -1})

    def test_add_invalid_member(self) -> None:
        '''Test add project member feature with invalid data.'''
        self.api_test(self.client.post, f'{self.endpoint}{self.project.id}/members/', 400)          # User is required

    def test_remove_member(self) -> None:
        '''Test remove project member feature.'''
        # Add member to the testing project
        self.api_test(self.client.post, f'{self.endpoint}{self.project.id}/members/', 201, data={'user': self.other.id})
        # Remove project member
        self.api_test(self.client.delete, f'{self.endpoint}{self.project.id}/members/{self.other.id}/', 204)

    def test_remove_not_found_member(self) -> None:
        '''Test remove project member feature with not found user.'''
        # Remove unexisting member from testing project
        self.api_test(self.client.delete, f'{self.endpoint}{self.project.id}/members/0/', 404)

    def test_remove_invalid_member(self) -> None:
        '''Test remove project member feature with invalid data.'''
        # Project owner can't be removed
        self.api_test(self.client.delete, f'{self.endpoint}{self.project.id}/members/{self.admin.id}/', 400)

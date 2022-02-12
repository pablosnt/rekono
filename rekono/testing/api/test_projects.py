from testing.api.base import RekonoTestCase
from users.models import User


class ProjectsTest(RekonoTestCase):
    '''Test cases for Projects module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        data = {'name': 'Project Test', 'description': 'Project Test', 'tags': ['test']}
        self.project = self.api_test(self.rekono.post, '/api/projects/', 201, data, data)   # Create project for testing

    def test_create(self) -> None:
        '''Test project creation feature.'''
        data = {'name': 'New Test', 'description': 'New Test', 'tags': ['new']}
        self.api_test(self.rekono.post, '/api/projects/', 201, data, data)      # Create new project

    def test_delete(self) -> None:
        '''Test project deletion feature.'''
        self.api_test(self.rekono.delete, f'/api/projects/{self.project["id"]}/', 204)      # Delete new project

    def test_update(self) -> None:
        '''Test project update feature.'''
        data = {'name': 'Update Test', 'description': 'Update Test', 'tags': ['update']}
        # Update testing project
        self.api_test(self.rekono.put, f'/api/projects/{self.project["id"]}/', 200, data, data)

    def test_members(self) -> None:
        '''Test project members features.'''
        # Create user for testing
        self.user = User.objects.create(username='project', email='project@project.project', password='project')
        # Add member to the testing project
        self.api_test(self.rekono.post, f'/api/projects/{self.project["id"]}/members/', 201, {'user': self.user.id})
        # Add unexisting member to the testing project
        self.api_test(self.rekono.post, f'/api/projects/{self.project["id"]}/members/', 404, {'user': -1})
        # User is required
        self.api_test(self.rekono.post, f'/api/projects/{self.project["id"]}/members/', 400)
        # Remove project member
        self.api_test(self.rekono.delete, f'/api/projects/{self.project["id"]}/members/{self.user.id}/', 204)
        # Remove unexisting member from testing project
        self.api_test(self.rekono.delete, f'/api/projects/{self.project["id"]}/members/0/', 404)
        # Project owner can't be removed
        self.api_test(self.rekono.delete, f'/api/projects/{self.project["id"]}/members/{self.admin.id}/', 400)

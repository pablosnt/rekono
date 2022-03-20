from typing import Any, Dict
from unittest import mock

from testing.api.base import RekonoTestCase
from testing.mocks.defectdojo import (defect_dojo_error, defect_dojo_success,
                                      defect_dojo_success_multiple)


class RekonoTestCaseWithDDImports(RekonoTestCase):
    '''Base test case including tests for Defect-Dojo integration.'''

    def initialize_environment(self) -> None:
        '''Initialize environment for testing.'''
        if not self.initialized:
            super().initialize_environment()

    def dd_test(self, status: int, data: Dict[str, Any] = {}) -> None:
        '''Make Rekono API requests to test Defect-Dojo integration.

        Args:
            status (int): Expected HTTP status code
            data (Dict[str, Any], optional): Body data to include in the HTTP request. Defaults to {}.
        '''
        if hasattr(self, 'endpoint') and hasattr(self, 'dd_model'):             # Check if subclass is configured
            self.initialize_environment()                                       # Initialize environment
            # Test import of execution report in Defect-Dojo
            self.api_test(self.client.post, f'{self.endpoint}{self.dd_model.id}/defect-dojo-scans/', status, data=data)
            # Test import of findings in Defect-Dojo
            self.api_test(
                self.client.post,
                f'{self.endpoint}{self.dd_model.id}/defect-dojo-findings/',
                status,
                data=data
            )

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    def test_import_in_defect_dojo(self) -> None:
        '''Test Defect-Dojo import feature.'''
        self.dd_test(200, {'id': 1})                                            # Import in existing engagement
        self.dd_test(200, {'name': 'Engagement', 'description': 'Engagement'})  # Import in new engagement

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    def test_import_in_defect_dojo_with_product_id(self) -> None:
        '''Test Defect-Dojo import feature when Rekono project has a related Defect-Dojo product.'''
        if hasattr(self, 'endpoint') and hasattr(self, 'dd_model'):             # Check if subclass is configured
            self.initialize_environment()                                       # Initialize environment
            self.project.defectdojo_product_id = 1                              # Save Defect-Dojo product Id in project
            self.project.save(update_fields=['defectdojo_product_id'])
            self.dd_test(200, {'id': 1})                                        # Import in existing engagement
            self.dd_test(200, {'name': 'Engagement', 'description': 'Engagement'})  # Import in new engagement

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo responses
    @mock.patch('defectdojo.api.DefectDojo.get_rekono_product_type', defect_dojo_success_multiple)
    def test_import_in_defect_dojo_with_existing_product_type(self) -> None:
        '''Test Defect-Dojo import feature when the Rekono product type already exists.'''
        # Import in new engagement
        self.dd_test(200, {'name': 'Engagement', 'description': 'Engagement using existing product type'})

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo responses
    @mock.patch('defectdojo.api.DefectDojo.get_rekono_test_type', defect_dojo_success_multiple)
    def test_import_in_defect_dojo_with_existing_test_type(self) -> None:
        '''Test Defect-Dojo import feature when the Rekono test type already exists.'''
        self.dd_test(200, {'id': 1})                                            # Import in new engagement
        # Import in new engagement
        self.dd_test(200, {'name': 'Engagement', 'description': 'Engagement using existing test type'})

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo responses
    @mock.patch('defectdojo.api.DefectDojo.create_rekono_product_type', defect_dojo_error)
    def test_import_in_defect_dojo_with_error_on_product_type_creation(self) -> None:
        '''Test Defect-Dojo import feature when product type creation fails.'''
        self.dd_test(400, {'name': 'Engagement', 'description': 'Engagement'})  # Try to import in new engagement

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo responses
    @mock.patch('defectdojo.api.DefectDojo.create_rekono_test_type', defect_dojo_error)
    def test_import_in_defect_dojo_with_error_on_test_type_creation(self) -> None:
        '''Test Defect-Dojo import feature when test type creation fails.'''
        if hasattr(self, 'endpoint') and hasattr(self, 'dd_model'):             # Check if subclass is configured
            self.initialize_environment()                                       # Initialize environment
            data = {'name': 'Engagement', 'description': 'Engagement'}
            # Try to import in new engagement
            self.api_test(self.client.post, f'{self.endpoint}{self.dd_model.id}/defect-dojo-findings/', 400, data=data)

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_error)         # Mocks Defect-Dojo response
    def test_import_in_defect_dojo_engagement_not_found(self) -> None:
        '''Test Defect-Dojo import featue when engagement is not found.'''
        self.dd_test(400, {'id': 1})                                            # Try to import in existing engagement

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo response
    def test_import_in_invalid_defect_dojo_engagement(self) -> None:
        '''Test Defect-Dojo import feature when engagement doesn't belong to product assciated to the Rekono project.'''
        if hasattr(self, 'endpoint') and hasattr(self, 'dd_model'):             # Check if subclass is configured
            self.initialize_environment()                                       # Initialize environment
            self.project.defectdojo_product_id = 2                              # Engagement belongs to product 1
            self.project.save(update_fields=['defectdojo_product_id'])
            self.dd_test(400, {'id': 1})                                        # Try to import in existing engagement

    @mock.patch('defectdojo.api.DefectDojo.request', defect_dojo_success)       # Mocks Defect-Dojo responses
    @mock.patch('defectdojo.api.DefectDojo.create_engagement', defect_dojo_error)
    def test_import_in_defect_dojo_with_error_on_engagement_creation(self) -> None:
        '''Test Defect-Dojo import featue when engagement creation fails.'''
        self.dd_test(400, {'name': 'Engagement', 'description': 'Engagement'})  # Try to import in new engagement

    def test_invalid_import_in_defect_dojo(self) -> None:
        '''Test Defect-Dojo import featue with invalid data.'''
        self.dd_test(400)                                                       # Id or (name and description) required
        self.dd_test(400, {'name': 'Engagement'})                               # Description required
        self.dd_test(400, {'name': 'Invalid#name', 'description': 'Invalid;description'})   # Invalid values
        self.dd_test(400, {'name': 'Valid name', 'description': 'Invalid;description'})     # Invalid description value

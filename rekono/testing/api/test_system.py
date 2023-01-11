from testing.api.base import RekonoApiTestCase


class SystemTestCase(RekonoApiTestCase):
    '''Test cases for System module.'''

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        self.endpoint = '/api/system/1/'                                        # System API endpoint
        self.system_data = {                                                    # Current system data
            'id': self.system.id,
            'upload_files_max_mb': self.system.upload_files_max_mb,
            'telegram_bot_token': self.system.telegram_bot_token,
            'defect_dojo_url': self.system.defect_dojo_url,
            'defect_dojo_api_key': self.system.defect_dojo_api_key,
            'defect_dojo_verify_tls': self.system.defect_dojo_verify_tls,
            'defect_dojo_tag': self.system.defect_dojo_tag,
            'defect_dojo_product_type': self.system.defect_dojo_product_type,
            'defect_dojo_test_type': self.system.defect_dojo_test_type,
            'defect_dojo_test': self.system.defect_dojo_test
        }

    def test_get_system(self) -> None:
        '''Test get system feature.'''
        self.api_test(self.client.get, self.endpoint, expected=self.system_data)    # Get system config

    def test_update_system(self) -> None:
        '''Test update system feature.'''
        new_system = self.system_data.copy()
        new_system['upload_files_max_mb'] = 128                                 # New max size for uploaded files
        new_system['telegram_bot_token'] = '1111111111:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'     # New Telegram token
        expected = new_system.copy()
        # Expected obfuscated Telegram token
        expected['telegram_bot_token'] = '**********************************************'
        new_system.pop('id')                                                    # Remove some fields from the new data
        new_system.pop('defect_dojo_api_key')
        self.api_test(self.client.put, self.endpoint, data=new_system, expected=expected)   # Update system config

    def test_invalid_update_system(self) -> None:
        '''Test update system feature with invalid data.'''
        new_system = self.system_data.copy()
        new_system['telegram_bot_token'] = 'invalidtelegramtoken'               # Invalid Telegram token
        self.api_test(self.client.put, self.endpoint, 400, data=new_system)     # Try to update system config

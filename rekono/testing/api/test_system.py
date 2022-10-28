from testing.api.base import RekonoApiTestCase


class SystemTestCase(RekonoApiTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.endpoint = '/api/system/1/'
        self.system_data = {
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
        self.api_test(self.client.get, self.endpoint, expected=self.system_data)

    def test_update_system(self) -> None:
        new_system = self.system_data.copy()
        new_system['upload_files_max_mb'] = 128
        new_system['telegram_bot_token'] = '1111111111:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        expected = new_system.copy()
        expected['telegram_bot_token'] = '**********************************************'
        new_system.pop('id')
        new_system.pop('defect_dojo_api_key')
        self.api_test(self.client.put, self.endpoint, data=new_system, expected=expected)

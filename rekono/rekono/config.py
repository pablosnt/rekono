from typing import Any, Dict, List

import yaml
from security.crypto import generate_random_value


class RekonoConfig:
    '''Rekono config loader from configuration file.'''

    def __init__(self, filepath: str) -> None:
        '''Rekono config constructor.

        Args:
            filepath (str): Configuration filepath
        '''
        config = {}
        if filepath:
            with open(filepath, 'r') as config_file:                            # Read configuration file
                config = yaml.safe_load(config_file)                            # Load configuration
        # Rekono frontend URL
        self.FRONTEND_URL = self.get_config_key(config, ['frontend', 'url'], 'http://127.0.0.1:8080')
        # Security
        self.SECRET_KEY = self.get_config_key(config, ['security', 'secret-key'], generate_random_value(3000))
        self.JWT_SIGNING_KEY = self.get_config_key(config, ['security', 'jwt-key'], generate_random_value(3000))
        self.UPLOAD_FILES_MAX_MB = self.get_config_key(config, ['security', 'upload-files-max-mb'], 500)
        self.OTP_EXPIRATION_HOURS = self.get_config_key(config, ['security', 'otp-expiration-hours'], 24)
        # Database
        self.DB_NAME = self.get_config_key(config, ['database', 'name'], 'rekono')
        self.DB_USER = self.get_config_key(config, ['database', 'user'], '')
        self.DB_PASSWORD = self.get_config_key(config, ['database', 'password'], '')
        self.DB_HOST = self.get_config_key(config, ['database', 'host'], '127.0.0.1')
        self.DB_PORT = self.get_config_key(config, ['database', 'port'], 5432)
        # Redis Queue
        self.RQ_HOST = self.get_config_key(config, ['rq', 'host'], '127.0.0.1')
        self.RQ_PORT = self.get_config_key(config, ['rq', 'port'], 6379)
        # Email: SMTP configuration
        self.EMAIL_HOST = self.get_config_key(config, ['email', 'host'], '')
        self.EMAIL_PORT = self.get_config_key(config, ['email', 'port'], 0)
        self.EMAIL_USER = self.get_config_key(config, ['email', 'user'], '')
        self.EMAIL_PASSWORD = self.get_config_key(config, ['email', 'password'], '')
        self.EMAIL_TLS = self.get_config_key(config, ['email', 'tls'], True)
        # Telegram Bot token
        self.TELEGRAM_TOKEN = self.get_config_key(config, ['telegram', 'token'], '')
        # Defect-Dojo
        self.DD_URL = self.get_config_key(config, ['defect-dojo', 'url'], 'http://127.0.0.1:8080')
        self.DD_API_KEY = self.get_config_key(config, ['defect-dojo', 'api-key'], '')
        self.DD_TAGS = self.get_config_key(config, ['defect-dojo', 'tags'], ['rekono'])
        self.DD_PRODUCT_AUTO_CREATION = self.get_config_key(config, ['defect-dojo', 'product', 'auto-creation'], True)
        self.DD_PRODUCT_TYPE = self.get_config_key(config, ['defect-dojo', 'product-type'], 'Rekono Project')
        self.DD_TEST_TYPE = self.get_config_key(config, ['defect-dojo', 'test-type'], 'Rekono Findings Import')
        self.DD_TEST = self.get_config_key(config, ['defect-dojo', 'test'], 'Rekono Test')
        # Tools
        self.TOOLS_CMSEEK_DIR = self.get_config_key(config, ['tools', 'cmseek', 'directory'], '/usr/share/cmseek')

    def get_config_key(self, config: Dict[str, Any], path: List[str], default: Any) -> Any:
        '''Get configuration value by dict path. Default value will be returned if value not found or it's null.

        Args:
            config (Dict[str, Any]): Configuration data
            path (List[str]): Path to the configuration value
            default (Any): Default value

        Returns:
            Any: Configuration value to apply
        '''
        value = config
        for key in path:
            value = value.get(key, {})
            if not value:                                                       # Value not found
                return default                                                  # Return default value
        return value

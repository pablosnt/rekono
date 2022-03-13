import os
from typing import Any, Dict, List

import yaml
from security.crypto import generate_random_value


class RekonoConfigLoader:
    '''Rekono config loader from configuration file.'''

    frontend_env_filename = '.env'                                              # Frontend environment file

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
        self.ALLOWED_HOSTS = self.get_config_key(config, ['security', 'allowed-hosts'], ['.ocalhost', '127.0.0.1', '::1'])    # noqa: E501
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
        self.EMAIL_HOST = self.get_config_key(config, ['email', 'host'], '127.0.0.1')
        self.EMAIL_PORT = self.get_config_key(config, ['email', 'port'], 587)
        self.EMAIL_USER = self.get_config_key(config, ['email', 'user'], None)
        self.EMAIL_PASSWORD = self.get_config_key(config, ['email', 'password'], None)
        self.EMAIL_TLS = self.get_config_key(config, ['email', 'tls'], True)
        # Telegram Bot token
        self.TELEGRAM_BOT = self.get_config_key(config, ['telegram', 'bot'], 'Rekono')
        self.TELEGRAM_TOKEN = self.get_config_key(config, ['telegram', 'token'], '')
        # Defect-Dojo
        self.DD_URL = self.get_config_key(config, ['defect-dojo', 'url'], 'http://127.0.0.1:8080')
        self.DD_API_KEY = self.get_config_key(config, ['defect-dojo', 'api-key'], '')
        self.DD_VERIFY_TLS = self.get_config_key(config, ['defect-dojo', 'verify'], True)
        self.DD_TAGS = self.get_config_key(config, ['defect-dojo', 'tags'], ['rekono'])
        self.DD_PRODUCT_AUTO_CREATION = self.get_config_key(config, ['defect-dojo', 'product', 'auto-creation'], True)
        self.DD_PRODUCT_TYPE = self.get_config_key(config, ['defect-dojo', 'product-type'], 'Rekono Project')
        self.DD_TEST_TYPE = self.get_config_key(config, ['defect-dojo', 'test-type'], 'Rekono Findings Import')
        self.DD_TEST = self.get_config_key(config, ['defect-dojo', 'test'], 'Rekono Test')
        # Tools
        self.TOOLS_CMSEEK_DIR = self.get_config_key(config, ['tools', 'cmseek', 'directory'], '/usr/share/cmseek')
        self.TOOLS_LOG4J_SCANNER_DIR = self.get_config_key(
            config,
            ['tools', 'log4j-scanner', 'directory'],
            '/opt/log4j-scanner'
        )
        self.TOOLS_GITTOOLS_DIR = self.get_config_key(config, ['tools', 'gittools', 'directory'], '/opt/GitTools')

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
            if key not in value or value.get(key) is None:                      # Value not found
                return default                                                  # Return default value
            value = value.get(key, {})
        return value

    def load_config_in_frontend(self, frontend: str, config: Dict[str, Any]) -> None:
        '''Load configuration values in frontend .env file.

        Args:
            frontend (str): Frontend directory
            config (Dict[str, Any]): Configuration keys and values
        '''
        if os.path.isdir(frontend):                                             # If frontend directory is found
            frontend_env_filepath = os.path.join(frontend, self.frontend_env_filename)      # Path to .env file
            with open(frontend_env_filepath, 'a') as frontend_env:              # Open .env file
                frontend_env.truncate(0)                                        # Clear .env content
                # Save frontend configuration
                frontend_env.write('\n'.join([f'{key}={value}' for key, value in config.items()]))

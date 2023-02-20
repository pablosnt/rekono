from typing import Any, Dict, List

import yaml
from security.crypto import generate_random_value


class RekonoConfigLoader:
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
        self.FRONTEND_URL = self.get_config_key(config, ['frontend', 'url'], 'https://127.0.0.1')
        # Rekono root path
        self.ROOT_PATH = self.get_config_key(config, ['rootpath'])
        # Security
        self.SECRET_KEY = self.get_config_key(config, ['security', 'secret-key'], generate_random_value(3000))
        self.ALLOWED_HOSTS = self.get_config_key(
            config,
            ['security', 'allowed-hosts'],
            ['localhost', '127.0.0.1', '::1']
        )
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
        self.EMAIL_HOST = self.get_config_key(config, ['email', 'host'])
        self.EMAIL_PORT = self.get_config_key(config, ['email', 'port'])
        self.EMAIL_USER = self.get_config_key(config, ['email', 'user'])
        self.EMAIL_PASSWORD = self.get_config_key(config, ['email', 'password'])
        self.EMAIL_TLS = self.get_config_key(config, ['email', 'tls'], True)
        # Tools
        self.TOOLS_CMSEEK_DIR = self.get_config_key(config, ['tools', 'cmseek', 'directory'], '/usr/share/cmseek')
        self.TOOLS_LOG4J_SCAN_DIR = self.get_config_key(
            config,
            ['tools', 'log4j-scan', 'directory'],
            '/opt/log4j-scan'
        )
        self.TOOLS_SPRING4SHELL_SCAN_DIR = self.get_config_key(
            config,
            ['tools', 'spring4shell-scan', 'directory'],
            '/opt/spring4shell-scan'
        )
        self.TOOLS_GITTOOLS_DIR = self.get_config_key(config, ['tools', 'gittools', 'directory'], '/opt/GitTools')

        # --------------------------------------------------------------------------------------------------------------
        # DEPRECATED
        # The following configurations are mantained for compatibility reasons with the previous version.
        # This support will be removed in the next release, since this settings can be managed using the Settings page.
        # --------------------------------------------------------------------------------------------------------------
        # Telegram Bot token
        self.TELEGRAM_TOKEN = self.get_config_key(config, ['telegram', 'token'])
        # Defect-Dojo
        self.DD_URL = self.get_config_key(config, ['defect-dojo', 'url'])
        self.DD_API_KEY = self.get_config_key(config, ['defect-dojo', 'api-key'])

    def get_config_key(self, config: Dict[str, Any], path: List[str], default: Any = None) -> Any:
        '''Get configuration value by dict path. Default value will be returned if value not found or it's null.

        Args:
            config (Dict[str, Any]): Configuration data
            path (List[str]): Path to the configuration value
            default (Any): Default value. By default None

        Returns:
            Any: Configuration value to apply
        '''
        value = config
        for key in path:
            if key not in value or value.get(key) is None:                      # Value not found
                return default                                                  # Return default value
            value = value.get(key, {})
        return value

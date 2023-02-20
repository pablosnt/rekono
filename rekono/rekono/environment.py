'''Environment variables used by Rekono.'''

# Rekono home directory
ENV_REKONO_HOME = 'REKONO_HOME'

# Rekono environment: indicate if Rekono is running with a trusted reverse proxy
RKN_TRUSTED_PROXY = 'RKN_TRUSTED_PROXY'
# Rekono frontend URL used to include links in notifications
RKN_FRONTEND_URL = 'RKN_FRONTEND_URL'
# Rekono root path to apply in API Rest documentation
RKN_ROOT_PATH = 'RKN_ROOT_PATH'

# Security configuration
RKN_SECRET_KEY = 'RKN_SECRET_KEY'
RKN_ALLOWED_HOSTS = 'RKN_ALLOWED_HOSTS'

# Database configuration
RKN_DB_NAME = 'RKN_DB_NAME'
RKN_DB_USER = 'RKN_DB_USER'
RKN_DB_PASSWORD = 'RKN_DB_PASSWORD'
RKN_DB_HOST = 'RKN_DB_HOST'
RKN_DB_PORT = 'RKN_DB_PORT'

# Redis Queue configuration
RKN_RQ_HOST = 'RKN_RQ_HOST'
RKN_RQ_PORT = 'RKN_RQ_PORT'

# SMTP configuration
RKN_EMAIL_HOST = 'RKN_EMAIL_HOST'
RKN_EMAIL_PORT = 'RKN_EMAIL_PORT'
RKN_EMAIL_USER = 'RKN_EMAIL_USER'
RKN_EMAIL_PASSWORD = 'RKN_EMAIL_PASSWORD'

# Tools configuration
RKN_CMSEEK_RESULTS = 'RKN_CMSEEK_RESULTS'
RKN_LOG4J_SCAN_DIR = 'RKN_LOG4J_SCAN_DIR'
RKN_GITTOOLS_DIR = 'RKN_GITTOOLS_DIR'
RKN_SPRING4SHELL_SCAN_DIR = 'RKN_SPRING4SHELL_SCAN_DIR'


# --------------------------------------------------------------------------------------------------------------
# DEPRECATED
# The following configurations are mantained for compatibility reasons with the previous version.
# This support will be removed in the next release, since this settings can be managed using the Settings page.
# --------------------------------------------------------------------------------------------------------------
# Telegram bot configuration
RKN_TELEGRAM_TOKEN = 'RKN_TELEGRAM_TOKEN'
# Defect-Dojo configuration
RKN_DD_URL = 'RKN_DD_URL'
RKN_DD_API_KEY = 'RKN_DD_API_KEY'

"""Django settings configuration for Rekono security testing platform.

This module contains the comprehensive Django settings configuration for the Rekono
platform, including database connections, security settings, API configuration,
authentication systems, and integration with external services and tools.

The configuration system supports both development and production environments with
secure defaults and extensive customization through environment variables and
configuration files managed by the RekonoConfig system.
"""

from datetime import timedelta
from typing import Any

from rekono.config import RekonoConfig

################################################################################
# Rekono basic information                                                     #
################################################################################

DESCRIPTION = "Offensive security platform that automates attack surface discovery and vulnerability management"
VERSION = "2.0.0"


################################################################################
# Load configuration                                                           #
################################################################################

CONFIG = RekonoConfig()


################################################################################
# Django                                                                       #
################################################################################

BASE_DIR = CONFIG.base_dir

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "django_rq",
    "drf_spectacular",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "taggit",
    "alerts",
    "api_tokens",
    "authentications",
    "executions",
    "findings",
    "http_headers",
    "input_types",
    "integrations",
    "monitor",
    "notes",
    "platforms.cvecrowd",
    "platforms.defectdojo",
    "platforms.email",
    "platforms.nvdnist",
    "platforms.telegram_app",
    "platforms.virustotal",
    "platforms.vulncheck",
    "parameters",
    "projects",
    "reporting",
    "security",
    "settings",
    "target_denylist",
    "target_ports",
    "targets",
    "tasks",
    "tools",
    # Processes MUST be loaded after tools, as their fixtures need configuration fixtures to be loaded first
    "processes",
    "wordlists",
    # Users MUST be loaded at the latest place, as it will load permissions fixtures from all the other models
    "users",
]

MIDDLEWARE = [
    "security.middleware.SecurityMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rekono.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "platforms" / "email" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "rekono.wsgi.application"


################################################################################
# Security                                                                     #
################################################################################

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG.secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = CONFIG.allowed_hosts

AUTH_USER_MODEL = "users.User"

# The Django built-in validators enforce baseline hygiene (not similar to the user's own data,
# a minimum length, not a common password, not fully numeric); PasswordValidator on top of them
# adds the actual complexity rules (mixed case, digit, symbol) required for Rekono accounts
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "security.validators.input_validator.PasswordValidator",
    },
]

# JWT configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "TOKEN_OBTAIN_SERIALIZER": "security.authentication.serializers.LoginSerializer",
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS512",
    "SIGNING_KEY": SECRET_KEY,
    "ISSUER": "Rekono",
}

# Cookies
JWT_ACCESS_COOKIE = "rekono_access"
JWT_REFRESH_COOKIE = "rekono_refresh"
JWT_MFA_COOKIE = "rekono_mfa"
COOKIES_CONFIG = {
    "httponly": True,
    "samesite": "None" if CONFIG.frontend_desktop else "Strict",
    "secure": CONFIG.secure_cookies,
}

LOGGING: dict[str, Any] = {
    "version": 1,
    # Disable default Django logging system to avoid noise
    "disable_existing_loggers": False,
    "formatters": {
        "rekono": {
            "format": "%(asctime)s [%(levelname)s] - %(process)d %(module)s - %(source_ip)s - %(user)s - %(message)s"
        }
    },
    "filters": {
        "rekono": {
            "()": "framework.logging.LoggingFilter",  # Custom logging filter
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "rekono",
            "filters": ["rekono"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": CONFIG.logs / "rekono.log",
            "maxBytes": 50 * 1024 * 1024,  # Max. 50 MB per file
            "backupCount": 10,
            "formatter": "rekono",
            "filters": ["rekono"],
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        }
    },
}


################################################################################
# API Rest                                                                     #
################################################################################

# nosemgrep: python.django.security.audit.django-rest-framework.missing-throttle-config.missing-throttle-config
REST_FRAMEWORK: dict[str, Any] = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_METADATA_CLASS": None,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "framework.pagination.Pagination",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "security.authentication.jwt.CookieJWTAuthentication",
        "security.authentication.api.ApiAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "security.authorization.permissions.RekonoModelPermission",
        "security.authorization.permissions.ProjectMemberPermission",
        "security.authorization.permissions.OwnerPermission",
    ],
    "EXCEPTION_HANDLER": "framework.exceptions.handler",
}
if not CONFIG.testing:
    # Rate limit only for production
    REST_FRAMEWORK.update(  # pragma: no cover
        {
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.AnonRateThrottle",  # Rate limit for anonymous users
                "rest_framework.throttling.UserRateThrottle",  # Rate limit for authenticated users
                "rest_framework.throttling.ScopedRateThrottle",  # Rate limit for specific cases
            ],
            "DEFAULT_THROTTLE_RATES": {
                # 2 requests by second by IP
                # To allow requests from different users with same public IP address
                # Note that most API requests requires authentication
                "anon": "100/min",
                # 17 request by second by user
                # It is enough for legitimate usage, but attacks will be blocked
                "user": "1000/min",
                # Prevent brute force attacks in login and refresh token features
                # Login is not authenticated, so many different users behind the same public IP
                # address count toward this same bucket
                "login": "30/min",
                # Same use case as login, just keeping an independent counter for each
                "refresh": "30/min",
                # MFA based on 6 digits is vulnerable to brute force attacks, we have to make it hard enough
                "mfa": "5/min",
            },
        }
    )

# Documentation
SPECTACULAR_SETTINGS = {
    "TITLE": "Rekono API Rest",
    "DESCRIPTION": DESCRIPTION,
    "VERSION": VERSION,
    "PREPROCESSING_HOOKS": ["drf_spectacular.hooks.preprocess_exclude_path_format"],
    "SCHEMA_PATH_PREFIX_INSERT": CONFIG.root_path,
    "ENUM_NAME_OVERRIDES": {
        "AuthenticationType": "authentications.enums.AuthenticationType",
        "PathType": "findings.enums.PathType",
        "PortStatus": "findings.enums.PortStatus",
        "TargetType": "targets.enums.TargetType",
        "TriageStatus": "findings.enums.TriageStatus",
        "WordlistType": "wordlists.enums.WordlistType",
        "TimeUnit": "tasks.enums.TimeUnit",
        "Status": "executions.enums.Status",
        "ReportStatus": "reporting.enums.ReportStatus",
    },
}


################################################################################
# Database                                                                     #
################################################################################

if CONFIG.testing:
    # In memory database for testing
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
else:
    # Production database
    DATABASES = {  # pragma: no cover
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": CONFIG.db_name,
            "USER": CONFIG.db_user,
            "PASSWORD": CONFIG.db_password,
            "HOST": CONFIG.db_host,
            "PORT": CONFIG.db_port,
        }
    }


################################################################################
# Redis Queues                                                                 #
################################################################################

default_rq_queue = {
    "HOST": CONFIG.rq_host,
    "PORT": CONFIG.rq_port,
    "DB": 0,
    "DEFAULT_TIMEOUT": 3600,  # 1 hour
}

# "tasks", "executions", and "findings" are the three stages of the scanning pipeline
# (a task plans executions, each execution produces findings); "monitor" runs periodic
# background jobs unrelated to a specific task. All queues share the same connection and
# default timeout, with "executions" and "findings" overridden below for longer-running jobs
RQ_QUEUES = {
    "tasks": default_rq_queue,
    "executions": default_rq_queue,
    "findings": default_rq_queue,
    "monitor": default_rq_queue,
    "cache": default_rq_queue,  # Not an RQ job queue; used by framework.cache.Cache to reuse this Redis connection
}

RQ_QUEUES["executions"]["DEFAULT_TIMEOUT"] = 86400  # 24 hours
RQ_QUEUES["findings"]["DEFAULT_TIMEOUT"] = 28800  # 8 hours

# Enqueue jobs immediately instead of deferring them until the database transaction commits.
# django-rq defaults to "on_db_commit", which returns None from enqueue() inside an atomic
# block (e.g. during tests or atomic requests), breaking the code that reads the resulting Job.
RQ = {"COMMIT_MODE": "auto"}


################################################################################
# Miscellaneous                                                                #
################################################################################

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
frontend_public = CONFIG.base_dir.parent / "frontend" / "public"
if frontend_public.exists():
    STATICFILES_DIRS = [frontend_public]
else:
    custom_static = CONFIG.base_dir / "static"
    custom_static.mkdir(exist_ok=True)
    STATICFILES_DIRS = [custom_static]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

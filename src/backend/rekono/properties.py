from enum import Enum

from security.crypto import generate_random_value


class Property(Enum):
    REKONO_HOME = ("REKONO_HOME", None, "/opt/rekono")
    FRONTEND_URL = ("RKN_FRONTEND_URL", "frontend.url", "https://127.0.0.1")
    ROOT_PATH = ("RKN_ROOT_PATH", "rootpath", None)
    SECRET_KEY = ("RKN_SECRET_KEY", "security.secret-key", generate_random_value(3000))
    ALLOWED_HOSTS = (
        "RKN_ALLOWED_HOSTS",
        "security.allowed-hosts",
        ["localhost", "127.0.0.1", "::1"],
    )
    TARGET_BLACKLIST = (
        None,
        None,
        [
            "127.0.0.1",
            "localhost",
            "frontend",
            "backend",
            "postgres",
            "redis",
            "initialize",
            "tasks-worker",
            "executions-worker",
            "findings-worker",
            "emails-worker",
            "telegram-bot",
            "nginx",
        ],
    )
    TRUSTED_PROXY = ("RKN_TRUSTED_PROXY", None, "false")
    DB_NAME = ("RKN_DB_NAME", "database.name", "rekono")
    DB_USER = ("RKN_DB_USER", "database.user", "")
    DB_PASSWORD = ("RKN_DB_PASSWORD", "database.password", "")
    DB_HOST = ("RKN_DB_HOST", "database.host", "127.0.0.1")
    DB_PORT = ("RKN_DB_PORT", "database.port", 5432)
    RQ_HOST = ("RKN_RQ_HOST", "rq.host", "127.0.0.1")
    RQ_PORT = ("RKN_RQ_PORT", "rq.port", 6379)
    SMTP_HOST = ("RKN_SMTP_HOST", "email.host", None)
    SMTP_PORT = ("RKN_SMTP_PORT", "email.port", None)
    SMTP_USER = ("RKN_SMTP_USER", "email.user", None)
    SMTP_PASSWORD = ("RKN_SMTP_PASSWORD", "email.password", None)
    SMTP_TLS = (None, "email.tls", True)
    CMSEEK_DIR = (
        "RKN_CMSEEK_RESULTS",
        "tools.cmseek.directory",
        "/usr/share/cmseek",
    )
    LOG4J_SCAN_DIR = (
        "RKN_LOG4J_SCAN_DIR",
        "tools.log4j-scan.directory",
        "/opt/log4j-scan",
    )
    SPRING4SHELL_SCAN_DIR = (
        "RKN_SPRING4SHELL_SCAN_DIR",
        "tools.spring4shell-scan.directory",
        "/opt/spring4shell-scan",
    )
    GITTOOLS_DIR = ("RKN_GITTOOLS_DIR", "tools.gittools.directory", "/opt/GitTools")

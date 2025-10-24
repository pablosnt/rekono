"""Role definitions and permission mappings for Rekono authorization.

Defines the role hierarchy and comprehensive permission mappings for all
models and operations within the Rekono platform. This module implements
role-based access control (RBAC) with fine-grained permissions for security,
compliance, and operational segregation of duties.
"""

from django.db import models
from django.db.models.enums import Choices


class Role(models.TextChoices):
    """Enumeration of user roles in the Rekono platform.

    Defines the hierarchical role structure for role-based access control.
    Each role represents a different level of access and operational capability
    within the security testing platform.

    Roles:
        ADMIN: System administrators with full access to all resources and operations.
               Can manage users, system settings, and perform all security operations.
        AUDITOR: Security auditors with read-write access to security data and findings.
                Can perform security testing, manage findings, and create reports.
        READER: Read-only users with access to security data and reports for review.
               Can view findings, reports, and security data but cannot modify them.

    Role Hierarchy:
        Admin > Auditor > Reader (in terms of access privileges)
    """

    ADMIN = "Admin"
    AUDITOR = "Auditor"
    READER = "Reader"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
Role: type[Choices] = Role

# Comprehensive role-based permission mapping for all Rekono models.
ROLES = {
    "apitoken": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR, Role.READER],
    },
    "user": {"view": [Role.ADMIN], "add": [Role.ADMIN], "change": [Role.ADMIN], "delete": [Role.ADMIN]},
    "project": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN],
        "change": [Role.ADMIN],
        "delete": [Role.ADMIN],
    },
    "target": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "targetport": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "targetdenylist": {"view": [Role.ADMIN], "add": [Role.ADMIN], "change": [Role.ADMIN], "delete": [Role.ADMIN]},
    "task": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "execution": {"view": [Role.ADMIN, Role.AUDITOR, Role.READER], "add": [], "change": [], "delete": []},
    "osint": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "host": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "port": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "path": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "technology": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "vulnerability": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "credential": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "exploit": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "process": {
        "view": [Role.ADMIN, Role.AUDITOR],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "step": {
        "view": [Role.ADMIN, Role.AUDITOR],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "tool": {"view": [Role.ADMIN, Role.AUDITOR], "add": [], "change": [], "delete": []},
    "intensity": {"view": [Role.ADMIN, Role.AUDITOR], "add": [], "change": [], "delete": []},
    "configuration": {"view": [Role.ADMIN, Role.AUDITOR], "add": [], "change": [], "delete": []},
    "input": {"view": [Role.ADMIN, Role.AUDITOR], "add": [], "change": [], "delete": []},
    "output": {"view": [Role.ADMIN, Role.AUDITOR], "add": [], "change": [], "delete": []},
    "wordlist": {
        "view": [Role.ADMIN, Role.AUDITOR],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "settings": {"view": [Role.ADMIN, Role.AUDITOR, Role.READER], "add": [], "change": [Role.ADMIN], "delete": []},
    "inputtype": {"view": [], "add": [], "change": [], "delete": []},
    "authentication": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "inputtechnology": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "inputvulnerability": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "defectdojosettings": {"view": [Role.ADMIN], "add": [], "change": [Role.ADMIN], "delete": []},
    "defectdojosync": {
        "view": [],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "defectdojotargetsync": {"view": [], "add": [], "change": [], "delete": []},
    "smtpsettings": {"view": [Role.ADMIN], "add": [], "change": [Role.ADMIN], "delete": []},
    "telegramsettings": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN],
        "delete": [],
    },
    "telegramchat": {
        "view": [],
        "add": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR, Role.READER],
    },
    "note": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "integration": {"view": [Role.ADMIN, Role.AUDITOR, Role.READER], "add": [], "change": [Role.ADMIN], "delete": []},
    "report": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR, Role.READER],
    },
    "httpheader": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "alert": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "change": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "delete": [Role.ADMIN, Role.AUDITOR, Role.READER],
    },
    "cvecrowdsettings": {"view": [Role.ADMIN], "add": [], "change": [Role.ADMIN], "delete": []},
    "monitorsettings": {"view": [Role.ADMIN], "add": [], "change": [Role.ADMIN], "delete": []},
    "nvdnistsettings": {"view": [Role.ADMIN], "add": [], "change": [Role.ADMIN], "delete": []},
    "virustotalsettings": {"view": [Role.ADMIN], "add": [], "change": [Role.ADMIN], "delete": []},
}

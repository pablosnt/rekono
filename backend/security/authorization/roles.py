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
        ADMIN: System administrators with full access to every model and operation,
               including user management, project management, and all platform settings.
        AUDITOR: Security auditors who can run security testing and manage findings.
                 They match Admin across most operational data, but cannot create,
                 modify or delete users and projects, cannot change any settings model,
                 and cannot see the Admin-only platform settings or the target denylist
                 at all.
        READER: Reviewers whose access is mostly limited to viewing findings, reports,
                and other security data. They can still manage their own notes, alerts,
                API tokens, reports, and Telegram chat registration.

    Role Hierarchy:
        Admin > Auditor > Reader. The nesting is strict, every permission granted to a
        role is also granted to the roles above it. Reader is nonetheless not a read-only
        role, since it holds write permissions on the personal resources listed above.
    """

    ADMIN = "Admin"
    AUDITOR = "Auditor"
    READER = "Reader"


# Type annotation workaround for pytype compatibility
# See: https://github.com/google/pytype/issues/1048
Role: type[Choices] = Role

# Role-based permission mapping for all Rekono models, as model name to action to the
# list of roles allowed to perform it. An empty list means no role can perform that
# action, which is how actions with no REST endpoint are expressed.
# These are coarse model-level permissions. Per-object scoping, such as restricting a
# user to their own notes or to the projects they belong to, is enforced separately by
# the permission classes in permissions.py and by the querysets in each ViewSet.
ROLES = {
    "apitoken": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR, Role.READER],
    },
    "user": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN],
        "change": [Role.ADMIN],
        "delete": [Role.ADMIN],
    },
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
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
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
    "tool": {"view": [Role.ADMIN, Role.AUDITOR, Role.READER], "add": [], "change": [], "delete": []},
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
    "defectdojosettings": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN],
        "delete": [],
    },
    "defectdojosync": {
        "view": [],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "defectdojotargetsync": {"view": [], "add": [], "change": [], "delete": []},
    "smtpsettings": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN],
        "delete": [],
    },
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
        "add": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "change": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "delete": [Role.ADMIN, Role.AUDITOR, Role.READER],
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
    "virustotalsettings": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN],
        "delete": [],
    },
    "vulnchecksettings": {"view": [Role.ADMIN], "add": [], "change": [Role.ADMIN], "delete": []},
}

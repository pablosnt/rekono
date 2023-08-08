from django.db import models
from typing import Dict, List


class Role(models.TextChoices):
    """User role names."""
    ADMIN = "Admin"
    AUDITOR = "Auditor"
    READER = "Reader"


PERMISSIONS = {
    "user": {
        "view": [Role.ADMIN],
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
    "task": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "execution": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [],
        "delete": [],
    },
    "osint": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "host": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "port": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "path": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "technology": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "vulnerability": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "credential": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "exploit": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [],
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
    "tool": {
        "view": [Role.ADMIN, Role.AUDITOR],
        "add": [],
        "change": [],
        "delete": [],
    },
    "intensity": {
        "view": [Role.ADMIN, Role.AUDITOR],
        "add": [],
        "change": [],
        "delete": [],
    },
    "configuration": {
        "view": [Role.ADMIN, Role.AUDITOR],
        "add": [],
        "change": [],
        "delete": [],
    },
    "input": {
        "view": [Role.ADMIN, Role.AUDITOR],
        "add": [],
        "change": [],
        "delete": [],
    },
    "output": {
        "view": [Role.ADMIN, Role.AUDITOR],
        "add": [],
        "change": [],
        "delete": [],
    },
    "wordlist": {
        "view": [Role.ADMIN, Role.AUDITOR],
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "system": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN],
        "delete": [],
    },
    "inputtype": {
        "view": [],
        "add": [],
        "change": [],
        "delete": [],
    },
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
}


def get_roles() -> Dict[Role, List[str]]:
    roles = {
        Role.ADMIN: [],
        Role.AUDITOR: [],
        Role.READER: [],
    }
    for entity, permissions in PERMISSIONS.items():
        for permission, assigned_roles in permissions.items():
            for assigned_role in assigned_roles:
                roles[assigned_role].append(f"{entity}_{permission}")
    return roles

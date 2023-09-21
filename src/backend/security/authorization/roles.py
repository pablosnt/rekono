from typing import Dict, List

from django.db import models


class Role(models.TextChoices):
    """User role names."""

    ADMIN = "Admin"
    AUDITOR = "Auditor"
    READER = "Reader"


PERMISSIONS = {
    "apitoken": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR, Role.READER],
    },
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
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [],
    },
    "host": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [],
    },
    "port": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [],
    },
    "path": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [],
    },
    "technology": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [],
    },
    "vulnerability": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [],
    },
    "credential": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [],
    },
    "exploit": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [],
    },
    # "process": {
    #     "view": [Role.ADMIN, Role.AUDITOR],
    #     "add": [Role.ADMIN, Role.AUDITOR],
    #     "change": [Role.ADMIN, Role.AUDITOR],
    #     "delete": [Role.ADMIN, Role.AUDITOR],
    # },
    # "step": {
    #     "view": [Role.ADMIN, Role.AUDITOR],
    #     "add": [Role.ADMIN, Role.AUDITOR],
    #     "change": [Role.ADMIN, Role.AUDITOR],
    #     "delete": [Role.ADMIN, Role.AUDITOR],
    # },
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
    "settings": {
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
        Role.ADMIN.value: [],
        Role.AUDITOR.value: [],
        Role.READER.value: [],
    }
    for entity, permissions in PERMISSIONS.items():
        for permission, assigned_roles in permissions.items():
            for assigned_role in assigned_roles:
                roles[assigned_role].append(f"{permission}_{entity}")
    return roles

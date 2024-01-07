from django.db import models


class Role(models.TextChoices):
    """User role names."""

    ADMIN = "Admin"
    AUDITOR = "Auditor"
    READER = "Reader"


ROLES = {
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
    "targetblacklist": {
        "view": [Role.ADMIN],
        "add": [Role.ADMIN],
        "change": [Role.ADMIN],
        "delete": [Role.ADMIN],
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
        "add": [Role.ADMIN, Role.AUDITOR],
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
    "defectdojosettings": {
        "view": [Role.ADMIN],
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
    "defectdojotargetsync": {
        "view": [],
        "add": [],
        "change": [],
        "delete": [],
    },
    "smtpsettings": {
        "view": [Role.ADMIN],
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
        "add": [Role.ADMIN, Role.AUDITOR],
        "change": [Role.ADMIN, Role.AUDITOR],
        "delete": [Role.ADMIN, Role.AUDITOR],
    },
    "integration": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [],
        "change": [Role.ADMIN],
        "delete": [],
    },
    "report": {
        "view": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "add": [Role.ADMIN, Role.AUDITOR, Role.READER],
        "change": [],
        "delete": [Role.ADMIN, Role.AUDITOR, Role.READER],
    },
}

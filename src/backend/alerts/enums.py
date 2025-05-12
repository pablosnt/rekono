from enum import Enum  # https://github.com/google/pytype/issues/1048

from django.db.models import TextChoices


class AlertItem(TextChoices, Enum):
    OSINT = "OSINT"
    HOST = "Host"
    OPEN_PORT = "Open Port"
    SERVICE = "Service"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    CVE = "CVE"


class AlertMode(TextChoices, Enum):
    NEW = "New"
    FILTER = "Filter"
    MONITOR = "Monitor"

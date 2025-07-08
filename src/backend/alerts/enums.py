from django.db.models import TextChoices
from django.db.models.enums import Choices


class AlertItem(TextChoices):
    OSINT = "OSINT"
    HOST = "Host"
    OPEN_PORT = "Open Port"
    SERVICE = "Service"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    CVE = "CVE"


class AlertMode(TextChoices):
    NEW = "New"
    FILTER = "Filter"
    MONITOR = "Monitor"


# https://github.com/google/pytype/issues/1048
AlertItem: type[Choices] = AlertItem
AlertMode: type[Choices] = AlertMode

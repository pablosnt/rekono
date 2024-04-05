from django.db.models import TextChoices


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

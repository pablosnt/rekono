# from enum import Enum  # https://github.com/google/pytype/issues/1048

from django.db.models import TextChoices


class FindingName(TextChoices):
    OSINT = "OSINT"
    HOST = "Host"
    PORT = "Port"
    PATH = "Path"
    TECHNOLOGY = "Technology"
    CREDENTIAL = "Credential"
    VULNERABILITY = "Vulnerability"
    EXPLOIT = "Exploit"


class ReportFormat(TextChoices):
    JSON = "json"
    XML = "xml"
    PDF = "pdf"


class ReportStatus(TextChoices):
    READY = "Ready"
    PENDING = "Pending"
    ERROR = "Error"
